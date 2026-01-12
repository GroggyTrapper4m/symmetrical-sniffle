from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def welcome(request):
    return HttpResponse("""
        <html>
            <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
                <h1>Legeacy App is now Running!</h1>
                <p>.... but should it be? </po>
                <p>Default view on our legacy project that might need updating.</p>
                        
                <a href="/admin">Go to Admin Interface</a>
            </body>
        </html>
    """)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', welcome),
]