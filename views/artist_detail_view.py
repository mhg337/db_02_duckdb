import flet as ft
from database import get_artist_by_id, get_albums_by_artist, get_tracks_by_album, get_reviews_by_album

def artist_detail_view(page, artist_id):
    artist = get_artist_by_id(int(artist_id))
    if not artist:
        return ft.View(route=f"/artist/{artist_id}", controls=[ft.Text("아티스트를 찾을 수 없습니다.")])
    
    _, artist_name, debut_date, country = artist
    albums = get_albums_by_artist(int(artist_id))

    album_title_text = ft.Text("앨범을 선택해 주세요", size=18, weight="bold")
    current_album_id = [None]

    # 1. 수록곡과 리뷰를 담을 리스트 (내용물)
    track_list_container = ft.Column(scroll="auto", expand=True)
    review_list_container = ft.Column(scroll="auto", expand=True, spacing=15)

    # --- 💡 무적의 커스텀 탭 로직 (버전 에러 0% 보장) ---
    # 각각의 리스트를 컨테이너 상자로 감싸줍니다.
    track_wrapper = ft.Container(content=track_list_container, expand=True, visible=True)
    review_wrapper = ft.Container(content=review_list_container, expand=True, visible=False)

    # 버튼을 누르면 보이는 상자를 스위치(Switch)하는 함수입니다.
    def click_track_tab(e):
        track_wrapper.visible = True
        review_wrapper.visible = False
        tab_track_btn.disabled = True   # 현재 보고 있는 탭의 버튼은 비활성화(회색)
        tab_review_btn.disabled = False
        if e: page.update()

    def click_review_tab(e):
        track_wrapper.visible = False
        review_wrapper.visible = True
        tab_track_btn.disabled = False
        tab_review_btn.disabled = True  # 현재 보고 있는 탭의 버튼은 비활성화(회색)
        if e: page.update()

    # 탭 역할을 할 두 개의 튼튼한 버튼
    tab_track_btn = ft.ElevatedButton("🎵 수록곡 보기", on_click=click_track_tab)
    tab_review_btn = ft.ElevatedButton("💬 리뷰 보기", on_click=click_review_tab)

    # 커스텀 탭 구역을 하나로 조립 (처음엔 숨겨둠)
    custom_tabs_area = ft.Column([
        ft.Row([tab_track_btn, tab_review_btn]), # 버튼들 가로로 배치
        ft.Divider(height=1),                    # 구분선
        track_wrapper,                           # 수록곡 상자
        review_wrapper                           # 리뷰 상자
    ], expand=True, visible=False)
    # ----------------------------------------------------

    def go_back(e):
        page.route = "/"
        page.on_route_change(None)

    def go_to_review(e):
        if current_album_id[0] is not None:
            page.route = f"/review/{current_album_id[0]}"
            page.on_route_change(None)

    review_btn = ft.ElevatedButton("⭐ 리뷰 작성하기", icon="edit", color="black", bgcolor="white", visible=False, on_click=go_to_review)

    # 왼쪽 앨범 클릭 시 실행
    def select_album(album_id, album_title):
        current_album_id[0] = album_id
        album_title_text.value = album_title
        review_btn.visible = True
        custom_tabs_area.visible = True # 💡 앨범을 누르면 커스텀 탭 등장!
        
        # --- 수록곡 데이터 채우기 ---
        tracks = get_tracks_by_album(album_id)
        track_list_container.controls.clear()
        if not tracks:
            track_list_container.controls.append(ft.Text("수록곡 정보가 없습니다.", italic=True))
        else:
            for t in tracks:
                t_id, _, t_num, t_title, duration, p_url = t
                mins, secs = divmod(duration, 60)
                track_list_container.controls.append(
                    ft.ListTile(leading=ft.Text(str(t_num), weight="bold"), title=ft.Text(t_title), subtitle=ft.Text(f"{mins}:{secs:02d}"))
                )

        # --- 리뷰 데이터 채우기 ---
        reviews = get_reviews_by_album(album_id)
        review_list_container.controls.clear()
        if not reviews:
            review_list_container.controls.append(ft.Text("아직 작성된 리뷰가 없습니다. 첫 리뷰를 남겨보세요!", size=16, color="grey", italic=True))
        else:
            for r in reviews:
                rating, comment, created_at = r
                date_str = str(created_at).split('.')[0]
                review_list_container.controls.append(
                    ft.Container(
                        padding=15, bgcolor="white", border=ft.border.all(1, "grey300"), border_radius=8,
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"⭐ {rating}점", weight="bold", size=16, color="orange"),
                                ft.Text(date_str, size=12, color="grey")
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Divider(height=1, color="grey200"),
                            ft.Text(comment, size=15)
                        ])
                    )
                )
        
        # 앨범을 누를 때마다 기본적으로 수록곡이 먼저 보이게 설정
        click_track_tab(None)
        page.update()

    album_controls = []
    for ab in albums:
        ab_id, _, ab_title, ab_date, cover_path = ab
        album_controls.append(
            ft.Card(
                content=ft.Container(
                    padding=10,
                    on_click=lambda e, a_id=ab_id, title=ab_title: select_album(a_id, title),
                    content=ft.Row([
                        ft.Image(src=cover_path, width=60, height=60, fit="cover", border_radius=4),
                        ft.Column([ft.Text(ab_title, size=14, weight="bold", max_lines=1, overflow="ellipsis", width=200), ft.Text(f"발매일: {ab_date}", size=12)], expand=True)
                    ]),
                )
            )
        )

    return ft.View(
        route=f"/artist/{artist_id}",
        appbar=ft.AppBar(
            leading=ft.TextButton("뒤로가기", icon="arrow_back", on_click=go_back, style=ft.ButtonStyle(color="black")),
            title=ft.Text(f"🎵 {artist_name} 상세 정보"),
            bgcolor="grey200"
        ),
        controls=[
            ft.Container(
                padding=15, bgcolor="grey100", border_radius=8,
                content=ft.Column([
                    ft.Text(artist_name, size=24, weight="bold"),
                    ft.Text(f"국적: {country}  |  데뷔일: {debut_date}", size=14),
                ])
            ),
            ft.Divider(),
            
            ft.Text("💿 수집된 앨범 목록 (클릭 시 수록곡 조회)", size=16, weight="bold"),
            ft.Container(
                expand=True,
                content=ft.Row([
                    ft.Container(content=ft.Column(album_controls, scroll="auto"), expand=1),
                    ft.VerticalDivider(),
                    ft.Container(
                        content=ft.Column([
                            ft.Row([album_title_text, review_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Divider(),
                            custom_tabs_area # 💡 에러 덩어리 ft.Tabs 대신, 우리가 만든 무적의 커스텀 탭 배치
                        ]), 
                        expand=1
                    )
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START)
            )
        ]
    )