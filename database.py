import duckdb
from pathlib import Path
import uuid

# DB 경로 설정
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "data" / "albumdate.db"

def get_connection(read_only=True):
    """DB 연결을 생성해서 반환합니다."""
    return duckdb.connect(str(DB_PATH), read_only=read_only)

def get_all_artists():
    """모든 아티스트 목록을 가져옵니다."""
    con = get_connection()
    rows = con.execute("SELECT artist_id, name, debut_date, country FROM Artists ORDER BY artist_id").fetchall()
    con.close()
    return rows

def get_album_detail(album_id):
    """앨범 상세 정보와 해당 아티스트 이름을 JOIN하여 가져옵니다."""
    con = get_connection()
    row = con.execute("""
        SELECT A.album_id, A.title, A.release_data, AR.name as artist_name
        FROM Albums A
        JOIN Artists AR ON A.artist_id = AR.artist_id
        WHERE A.album_id = ?
    """, (album_id,)).fetchone()
    con.close()
    return row

def get_artist_by_id(artist_id):
    """특정 아티스트의 정보를 가져옵니다."""
    con = duckdb.connect(str(DB_PATH))
    result = con.execute("SELECT * FROM Artists WHERE artist_id = ?", (artist_id,)).fetchone()
    con.close()
    return result

def get_albums_by_artist(artist_id):
    """해당 아티스트의 모든 앨범을 최신순으로 가져옵니다."""
    con = duckdb.connect(str(DB_PATH))
    result = con.execute("SELECT * FROM Albums WHERE artist_id = ? ORDER BY release_data DESC", (artist_id,)).fetchall()
    con.close()
    return result

def get_tracks_by_album(album_id):
    """해당 앨범의 수록곡들을 트랙 번호 순서대로 가져옵니다."""
    con = duckdb.connect(str(DB_PATH))
    result = con.execute("SELECT * FROM Tracks WHERE album_id = ? ORDER BY track_number", (album_id,)).fetchall()
    con.close()
    return result

def init_reviews_table():
    """평가(Reviews) 테이블이 없으면 생성합니다."""
    con = duckdb.connect(str(DB_PATH))
    con.execute("""
        CREATE TABLE IF NOT EXISTS Reviews (
            review_id VARCHAR PRIMARY KEY,
            album_id BIGINT,
            rating INTEGER,
            comment VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.close()

def get_reviews_by_album(album_id):
    """특정 앨범에 달린 평가 목록을 최신순으로 가져옵니다."""
    con = duckdb.connect(str(DB_PATH))
    result = con.execute("SELECT rating, comment, created_at FROM Reviews WHERE album_id = ? ORDER BY created_at DESC", (album_id,)).fetchall()
    con.close()
    return result

def add_review(album_id, rating, comment):
    """앨범에 새로운 평가를 추가합니다."""
    review_id = str(uuid.uuid4())
    con = duckdb.connect(str(DB_PATH))
    con.execute("INSERT INTO Reviews (review_id, album_id, rating, comment) VALUES (?, ?, ?, ?)", (review_id, album_id, rating, comment))
    con.close()