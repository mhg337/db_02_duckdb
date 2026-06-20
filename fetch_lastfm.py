import requests
import duckdb
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "data" / "albumdate.db"

def import_artist_music(artist_name):
    print(f"🎵 [Apple Music 완벽 모드] '{artist_name}' 데이터 수집 시작...")

    # 1. 가수 이름으로 정확한 고유 ID(artistId) 찾기
    search_url = f"https://itunes.apple.com/search?term={requests.utils.quote(artist_name)}&entity=musicArtist&country=KR&lang=ko_kr&limit=1"
    search_res = requests.get(search_url).json()
    
    if not search_res.get("results"):
        search_url = f"https://itunes.apple.com/search?term={requests.utils.quote(artist_name)}&entity=musicArtist&country=US&lang=ko_kr&limit=1"
        search_res = requests.get(search_url).json()
        
    if not search_res.get("results"):
        print("❌ 아티스트를 찾을 수 없습니다.")
        return

    artist_data = search_res["results"][0]
    artist_id = artist_data["artistId"]
    actual_name = artist_data["artistName"]
    primary_genre = artist_data.get("primaryGenreName", "")
    estimated_country = "대한민국" if "K-Pop" in primary_genre or "트로트" in primary_genre else "해외"

    # --- 💡 [수정됨] 2. 아티스트 등록 전, 앨범 목록을 먼저 가져와서 진짜 데뷔일 계산하기 ---
    albums_url = f"https://itunes.apple.com/lookup?id={artist_id}&entity=album&country=KR&lang=ko_kr&limit=25"
    albums_data = requests.get(albums_url).json().get("results", [])
    
    if len(albums_data) <= 1:
        albums_url = f"https://itunes.apple.com/lookup?id={artist_id}&entity=album&country=US&lang=ko_kr&limit=25"
        albums_data = requests.get(albums_url).json().get("results", [])

    # 수집된 앨범들의 날짜 중 가장 오래된 날짜(min) 찾기
    all_dates = []
    for item in albums_data:
        if item.get("wrapperType") == "collection":
            date_str = item.get("releaseDate", "")
            if date_str:
                all_dates.append(date_str[:10])
                
    actual_debut_date = min(all_dates) if all_dates else "발매일 미상"

    # DB 테이블 생성
    con = duckdb.connect(str(DB_PATH))
    con.execute("""
        CREATE TABLE IF NOT EXISTS Artists (artist_id BIGINT PRIMARY KEY, name VARCHAR, debut_date VARCHAR, country VARCHAR);
        CREATE TABLE IF NOT EXISTS Albums (album_id BIGINT PRIMARY KEY, artist_id BIGINT, title VARCHAR, release_data VARCHAR, cover_image_path VARCHAR);
        CREATE TABLE IF NOT EXISTS Tracks (track_id BIGINT PRIMARY KEY, album_id BIGINT, track_number INTEGER, title VARCHAR, duration INTEGER, preview_url VARCHAR);
    """)

    # 3. 이제 계산된 진짜 데뷔일(actual_debut_date)로 아티스트 정보 저장!
    con.execute("""
        INSERT INTO Artists (artist_id, name, debut_date, country) VALUES (?, ?, ?, ?)
        ON CONFLICT (artist_id) DO UPDATE SET 
            name = EXCLUDED.name, 
            country = EXCLUDED.country,
            debut_date = EXCLUDED.debut_date
    """, (artist_id, actual_name, actual_debut_date, estimated_country))
    print(f"✅ 아티스트 등록 완료: {actual_name} (데뷔일: {actual_debut_date} / 국적: {estimated_country})")

    # 4. 앨범 및 수록곡 데이터 삽입 진행
    for item in albums_data:
        if item.get("wrapperType") == "collection":
            album_id = item["collectionId"]
            album_title = item["collectionName"]
            release_date = item.get("releaseDate", "2000-01-01")[:10]
            cover_url = item.get("artworkUrl100", "").replace("100x100bb.jpg", "500x500bb.jpg")

            con.execute("""
                INSERT INTO Albums (album_id, artist_id, title, release_data, cover_image_path) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (album_id) DO UPDATE SET title = EXCLUDED.title, release_data = EXCLUDED.release_data, cover_image_path = EXCLUDED.cover_image_path
            """, (album_id, artist_id, album_title, release_date, cover_url))
            print(f"   💿 앨범: {album_title} ({release_date})")

            # 수록곡 추출 (KR -> US 우회 로직 동일)
            tracks_url = f"https://itunes.apple.com/lookup?id={album_id}&entity=song&country=KR&lang=ko_kr"
            tracks_data = requests.get(tracks_url).json().get("results", [])
            
            has_tracks = any(t.get("wrapperType") == "track" for t in tracks_data)
            if not has_tracks:
                tracks_url_us = f"https://itunes.apple.com/lookup?id={album_id}&entity=song&country=US&lang=ko_kr"
                tracks_data = requests.get(tracks_url_us).json().get("results", [])

            track_count = 0
            for track in tracks_data:
                if track.get("wrapperType") == "track":
                    track_id = track["trackId"]
                    track_title = track["trackName"]
                    track_num = track.get("trackNumber", track_count + 1)
                    time_millis = track.get("trackTimeMillis")
                    duration_secs = int(time_millis / 1000) if time_millis else 180
                    preview_url = track.get("previewUrl", "")

                    con.execute("""
                        INSERT INTO Tracks (track_id, album_id, track_number, title, duration, preview_url) VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT (track_id) DO UPDATE SET track_number = EXCLUDED.track_number, title = EXCLUDED.title, preview_url = EXCLUDED.preview_url
                    """, (track_id, album_id, track_num, track_title, duration_secs, preview_url))
                    track_count += 1
            
            if track_count > 0:
                print(f"      🍏 수록곡 {track_count}개 완벽 동기화 완료.")

    con.close()
    print("\n🎉 Apple Music 완벽 동기화 프로세스 완료!")