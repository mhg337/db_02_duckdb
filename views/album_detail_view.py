import flet as ft
# 💡 핵심: 저장된 리뷰를 불러오기 위해 get_reviews_by_album을 추가로 가져옵니다.
from database import get_tracks_by_album, get_reviews_by_album

def album_detail_view(page, album_id):
    # DB에서 수록곡과 리뷰 데이터를 모두 가져옵니다.
    tracks = get_tracks_by_album(int(album_id))
    reviews = get_reviews_by_album(int(album_id)) 

    def go_back(e):
        page.route = "/" 
        page.on_route_change(None)

    def go_to_review(e):
        page.route = f"/review/{album_id}"
        page.on_route_change(None)

    custom_appbar = ft.Container(
        padding=10,
        bgcolor="grey200",
        content=ft.Row([
            ft.TextButton("뒤로가기", icon="arrow_back", on_click=go_back, style=ft.ButtonStyle(color="black")),
            ft.Text("💿 앨범 상세 정보", size=20, weight="bold", expand=True), 
            ft.ElevatedButton("⭐ 리뷰 작성하기", icon="edit", on_click=go_to_review, color="black", bgcolor="white")
        ])
    )

    # --- 1. 첫 번째 탭: 수록곡 리스트 ---
    track_list = ft.Column(scroll="auto", expand=True)
    
    if not tracks:
        track_list.controls.append(ft.Text("수록곡 정보가 없습니다.", size=16))
    else:
        for track in tracks:
            _, _, track_number, track_title, duration, preview_url = track
            mins, secs = divmod(duration, 60)
            
            track_list.controls.append(
                ft.ListTile(
                    leading=ft.Text(str(track_number), size=16, weight="bold"),
                    title=ft.Text(track_title, size=16),
                    subtitle=ft.Text(f"{mins}:{secs:02d}"),
                    trailing=ft.Icon("audiotrack")
                )
            )

    # --- 💡 2. 두 번째 탭: 저장된 리뷰 리스트 ---
    review_list = ft.Column(scroll="auto", expand=True, spacing=15)
    
    if not reviews:
        review_list.controls.append(ft.Text("아직 작성된 리뷰가 없습니다. 첫 리뷰를 남겨보세요!", size=16, color="grey", italic=True))
    else:
        for r in reviews:
            # DB에 저장된 (점수, 코멘트, 작성시간)을 꺼내옵니다.
            rating, comment, created_at = r 
            date_str = str(created_at).split('.')[0] # 소수점 이하 시간은 깔끔하게 자르기
            
            # 리뷰 하나하나를 예쁜 박스(Container)에 담아서 보여줍니다.
            review_list.controls.append(
                ft.Container(
                    padding=15,
                    bgcolor="white",
                    border=ft.border.all(1, "grey300"),
                    border_radius=8,
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"⭐ {rating}점", weight="bold", size=16, color="orange"),
                            ft.Text(date_str, size=12, color="grey")
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), # 점수는 왼쪽, 시간은 오른쪽에 배치
                        ft.Divider(height=1, color="grey200"),
                        ft.Text(comment, size=15)
                    ])
                )
            )

    # --- 3. 탭(Tabs) 컴포넌트로 합치기 ---
    album_tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="🎵 수록곡",
                content=ft.Container(content=track_list, padding=20)
            ),
            ft.Tab(
                text="💬 유저 리뷰",
                content=ft.Container(content=review_list, padding=20, bgcolor="grey50")
            ),
        ],
        expand=True
    )

    return ft.View(
        route=f"/album/{album_id}",
        padding=0, 
        controls=[
            custom_appbar,
            album_tabs # 탭을 화면 전체에 꽉 차게 배치합니다.
        ]
    )