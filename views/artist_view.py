import flet as ft
from database import get_artist_by_id, get_albums_by_artist

def artist_detail_view(page: ft.Page, artist_id: str):
    artist = get_artist_by_id(int(artist_id))
    
    if not artist:
        return ft.View(route=f"/artist/{artist_id}", controls=[ft.Text("아티스트를 찾을 수 없습니다.")])

    a_id, name, debut, country = artist
    
    # 1. 아티스트의 앨범 목록 DB에서 가져오기
    albums = get_albums_by_artist(int(artist_id))
    
    album_list_view = ft.Row(wrap=True, spacing=20)
    
    def go_album(e, al_id):
        page.route = f"/album/{al_id}"
        page.on_route_change(None)

    if not albums:
        album_list_view.controls.append(ft.Text("등록된 앨범이 없습니다.", color=ft.Colors.GREY))
    else:
        for al in albums:
            # ✅ DB에서 이미지 경로까지 4개의 데이터를 받아옵니다.
            album_id, _, title, release_date, cover_path = al
            
            # (꿀팁) 로컬에 진짜 이미지가 아직 없으므로, 앨범 ID를 기반으로 예쁜 랜덤 사진을 생성하는 URL을 씁니다.
            # 나중에 진짜 사진을 쓰실 때는 src=cover_path 로 바꾸시면 됩니다!
            image_url = f"https://picsum.photos/seed/{album_id}/200/200"

            # 멜론/스포티파이 스타일의 앨범 카드 생성
            album_list_view.controls.append(
                ft.Card(
                    elevation=4,
                    bgcolor=ft.Colors.WHITE,
                    content=ft.Container(
                        width=180, # 카드의 전체 가로 너비
                        padding=15,
                        on_click=lambda e, a_id=album_id: go_album(e, a_id),
                        ink=True,
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER, # 카드 안의 내용을 가운데 정렬
                            spacing=10,
                            controls=[
                                # 1. 앨범 커버 이미지
                                ft.Image(
                                    src=image_url,
                                    width=150,
                                    height=150,
                                    fit="cover", # ✅ 직관적인 문자열로 변경!
                                    border_radius=ft.border_radius.all(10),
                                ),
                                # 2. 앨범 텍스트 (제목, 발매일)
                                ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=2,
                                    controls=[
                                        ft.Text(title, weight="bold", size=16, color=ft.Colors.BLACK, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                        ft.Text(f"발매일: {release_date}", size=12, color=ft.Colors.BLACK54),
                                    ]
                                )
                            ]
                        )
                    )
                )
            )
    return ft.View(
        route=f"/artist/{artist_id}",
        appbar=ft.AppBar(title=ft.Text(f"{name} 상세 정보"), bgcolor=ft.Colors.GREY_200),
        controls=[
            ft.Text(name, size=40, weight="bold"),
            ft.Card(
                content=ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Text(f"🆔 아티스트 ID: {a_id}"),
                        ft.Text(f"📅 데뷔일: {debut}"),
                        ft.Text(f"🌎 국가: {country}"),
                    ])
                )
            ),
            ft.Divider(height=30),
            ft.Text("💿 발매 앨범 목록", size=20, weight="bold"),
            # 3. 만들어둔 앨범 리스트 화면에 추가
            album_list_view 
        ],
        scroll="auto"
    )