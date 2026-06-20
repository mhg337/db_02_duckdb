import flet as ft
import duckdb
from database import DB_PATH, add_review

def review_view(page, album_id):
    con = duckdb.connect(str(DB_PATH))
    album_info = con.execute("""
        SELECT A.title, Ar.name
        FROM Albums A
        JOIN Artists Ar ON A.artist_id = Ar.artist_id
        WHERE A.album_id = ?
    """, (int(album_id),)).fetchone()
    con.close()

    album_title = album_info[0] if album_info else "알 수 없는 앨범"
    artist_name = album_info[1] if album_info else "알 수 없는 아티스트"

    def go_back(e):
        page.route = "/"
        page.on_route_change(None)

    # 💡 0/5점 선택 방식의 드롭다운 (아이콘 에러 원천 차단)
    score_dropdown = ft.Dropdown(
        label="점수 선택",
        width=150,
        options=[
            ft.dropdown.Option("5점 (최고)"),
            ft.dropdown.Option("4점"),
            ft.dropdown.Option("3점"),
            ft.dropdown.Option("2점"),
            ft.dropdown.Option("1점 (최악)"),
        ],
        value="5점 (최고)"
    )

    comment_input = ft.TextField(
        multiline=True,
        min_lines=6,
        hint_text="앨범 리뷰 코멘트 작성",
        border_color="black", 
        border_width=2
    )

    def save_click(e):
        if not comment_input.value.strip():
            page.overlay.append(ft.SnackBar(ft.Text("리뷰 내용을 입력해주세요!")))
            page.update()
            return
            
        # 점수 텍스트에서 숫자만 추출 (예: "5점" -> 5)
        rating = int(score_dropdown.value[0])
        add_review(int(album_id), rating, comment_input.value.strip())
        
        page.route = "/"
        page.on_route_change(None)

    return ft.View(
        route=f"/review/{album_id}",
        bgcolor="grey100", 
        appbar=ft.AppBar(
            leading=ft.TextButton("취소", icon="arrow_back", on_click=go_back, style=ft.ButtonStyle(color="black")),
            title=ft.Text("리뷰 작성 페이지"),
            bgcolor="grey200"
        ),
        controls=[
            ft.Container(
                padding=40,
                content=ft.Container(
                    bgcolor="white",
                    padding=30,
                    border=ft.border.all(2, "black"), 
                    content=ft.Column([
                        ft.Container(content=ft.Row([ft.Text("앨범 리뷰 남기기", size=20, weight="bold")], alignment=ft.MainAxisAlignment.CENTER), border=ft.border.all(1, "black"), padding=15),
                        ft.Container(height=10),
                        
                        ft.Container(content=ft.Row([ft.Text(f"{album_title} - {artist_name}", size=18)], alignment=ft.MainAxisAlignment.CENTER), border=ft.border.all(1, "black"), padding=15),
                        ft.Container(height=10),

                        # 💡 아이콘 대신 드롭다운으로 점수를 선택합니다.
                        ft.Row([
                            ft.Container(content=ft.Text("점수 선택:", size=16), border=ft.border.all(1, "black"), padding=10),
                            score_dropdown
                        ]),
                        ft.Container(height=10),

                        comment_input,
                        ft.Container(height=10),

                        ft.Row([
                            ft.OutlinedButton("저장", on_click=save_click, style=ft.ButtonStyle(color="black", shape=ft.RoundedRectangleBorder(radius=0)))
                        ], alignment=ft.MainAxisAlignment.END)
                    ])
                )
            )
        ]
    )