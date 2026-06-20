import flet as ft
from views.home_view import home_view
from views.artist_detail_view import artist_detail_view
from views.album_detail_view import album_detail_view
from views.review_view import review_view

def main(page: ft.Page):
    page.title = "Music Dashboard"
    page.theme_mode = ft.ThemeMode.LIGHT 
    
    page.window.width = 1000
    page.window.height = 800    

    def route_change(route):
        page.views.clear()
        
        if page.route == "/":
            page.views.append(home_view(page))
            
        elif page.route.startswith("/artist/"):
            artist_id = page.route.split("/")[-1]
            page.views.append(artist_detail_view(page, artist_id))
            
        elif page.route.startswith("/album/"):
            album_id = page.route.split("/")[-1]
            page.views.append(album_detail_view(page, album_id))
            
        # ✅ 새 페이지 이동 규칙 추가!
        elif page.route.startswith("/review/"):
            album_id = page.route.split("/")[-1]
            page.views.append(review_view(page, album_id))
            
        page.update()

    def view_pop(view):
        page.views.pop() 
        top_view = page.views[-1] 
        page.route = top_view.route
        page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.route = "/"
    route_change(None)

if __name__ == "__main__":
    ft.run(main)