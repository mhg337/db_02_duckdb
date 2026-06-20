import flet as ft
import os # 파일 삭제를 위한 라이브러리 추가
from database import get_all_artists
from fetch_lastfm import import_artist_music, DB_PATH # DB_PATH 가져오기

def home_view(page):

    def go_detail(e, artist_id):
        page.route = f"/artist/{artist_id}"
        page.on_route_change(None)

    search_input = ft.TextField(hint_text="새로운 가수 검색 (예: aespa, 아이유)", expand=True)
    loading_ring = ft.ProgressRing(width=20, height=20, visible=False)
    table_container = ft.Column(scroll="auto", expand=True)
    
    def refresh_table():
        try:
            artists = get_all_artists()
        except Exception:
            artists = [] # DB 파일이 삭제되었거나 테이블이 없을 때를 대비한 예외 처리
            
        rows = []
        for row in artists:
            artist_id, name, debut_date, country = row
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(artist_id))),
                        ft.DataCell(ft.Text(name)),
                        ft.DataCell(ft.Text(debut_date)),
                        ft.DataCell(ft.Text(country)),
                    ],
                    on_select_change=lambda e, a_id=artist_id: go_detail(e, a_id)
                )
            )
            
        data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("아티스트명")),
                ft.DataColumn(ft.Text("데뷔일")),
                ft.DataColumn(ft.Text("국가")),
            ],
            rows=rows
        )
        
        table_container.controls.clear()
        table_container.controls.append(data_table)
        page.update()

    def search_click(e):
        keyword = search_input.value.strip()
        if not keyword:
            return
            
        search_btn.disabled = True
        loading_ring.visible = True
        page.update()
        
        try:
            import_artist_music(keyword)
        except Exception as ex:
            print("데이터 수집 에러:", ex)
            
        search_input.value = ""
        search_btn.disabled = False
        loading_ring.visible = False
        refresh_table()

    def reset_db_click(e):
        # 1. 꼬여버린 기존 DB 파일을 물리적으로 삭제합니다.
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            
        # 2. 표를 새로고침하여 빈 화면으로 만듭니다.
        refresh_table()
        
        # 3. 사용자에게 알림창(SnackBar)을 띄웁니다.
        # ✅ 최신 Flet 표준 문법인 page.open() 방식으로 변경합니다.
        page.open(ft.SnackBar(ft.Text("데이터베이스가 깔끔하게 초기화되었습니다!")))

    search_btn = ft.ElevatedButton("검색 및 추가", icon="search", on_click=search_click)
    
    reset_btn = ft.OutlinedButton(
        "초기화",
        icon="delete",
        icon_color="red",
        on_click=reset_db_click
    )
    refresh_table()

    return ft.View(
        route="/",
        appbar=ft.AppBar(title=ft.Text("🎵 홈: 아티스트 목록"), bgcolor=ft.Colors.GREY_200),
        controls=[
            ft.Container(
                padding=10,
                # 검색바 옆에 휴지통 버튼(reset_btn)을 배치했습니다.
                content=ft.Row([search_input, search_btn, reset_btn, loading_ring], alignment=ft.MainAxisAlignment.CENTER)
            ),
            ft.Divider(),
            table_container
        ]
    )