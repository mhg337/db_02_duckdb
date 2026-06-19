import flet as ft
import duckdb
from pathlib import Path

def main(page: ft.Page):
    # 1. 페이지 기본 설정
    page.title = "음악 데이터베이스 관리자"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30

    # 2. UI 요소 준비: 제목과 데이터 테이블
    title = ft.Text("🎤 등록된 아티스트 목록", size=24, weight=ft.FontWeight.BOLD)
    
    # 엑셀처럼 데이터를 띄워줄 표(DataTable) 생성
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("아티스트명", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("데뷔일", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("국가", weight=ft.FontWeight.BOLD)),
        ],
        rows=[] # 데이터는 DB에서 읽어와서 이곳에 채울 예정입니다.
    )

    # 3. DB에서 데이터 불러오는 함수
    def load_data(e=None):
        BASE_DIR = Path(__file__).parent
        DB_PATH = BASE_DIR / "data" / "albumdate.db"
        
        try:
            # DB 연결 (읽기 전용 옵션 read_only=True를 주면 더 안전합니다)
            con = duckdb.connect(str(DB_PATH), read_only=True)
            
            # Artists 테이블의 모든 데이터 가져오기
            rows = con.execute("SELECT artist_id, name, debut_date, country FROM Artists ORDER BY artist_id").fetchall()
            
            # 기존 표에 있던 데이터 싹 비우기
            data_table.rows.clear()
            
            # DB에서 가져온 데이터를 표의 한 줄(Row)씩 만들어 추가하기
            for row in rows:
                data_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(row[0]))),
                        ft.DataCell(ft.Text(str(row[1]))),
                        ft.DataCell(ft.Text(str(row[2]))),
                        ft.DataCell(ft.Text(str(row[3]))),
                    ])
                )
            con.close()
            
            # 화면 새로고침
            page.update()
            
        except Exception as err:
            # 에러가 나면 화면 하단에 빨간 알림창 띄우기
            page.snack_bar = ft.SnackBar(ft.Text(f"DB 연결 에러 (디비버를 껐는지 확인하세요!): {err}", color="red"))
            page.snack_bar.open = True
            page.update()

    # 4. 새로고침 버튼
    refresh_btn = ft.ElevatedButton("새로고침", icon="refresh", on_click=load_data)

    # 5. 화면에 요소들 배치하기
    page.add(
        ft.Row([title, refresh_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(height=20, color=ft.Colors.GREY_300),
        data_table
    )

    # 6. 앱이 처음 켜질 때 자동으로 데이터 한 번 불러오기
    load_data()

if __name__ == "__main__":
    # 데스크톱 앱 모드로 실행
    ft.run(main)