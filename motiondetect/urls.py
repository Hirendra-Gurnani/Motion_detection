from django.urls import path
from . import views
from django.views.generic import TemplateView 

urlpatterns = [
    path("",views.signin,name="signin"),
    path("signup",views.signup,name="signup"),
    path("register",views.register,name="register"),
    path("second",views.second,name="second"),
    path("stop",views.stop,name="stop" ),
    path("start",views.start,name="start"),
    path("details",views.details,name="details"),
    path("deleted",views.deleted,name="deleted"),
    path("login_auth",views.login_auth,name="login_auth"),
    path("setting",views.setting,name="setting"),
    path("changepass",views.changepass,name="changepass"),
    path("admin",views.admin,name="admin"),
    path("admin_auth",views.admin_auth,name="admin_auth"),
    path("admin_signup",views.admin_signup,name="admin_signup"),
    path("a_signup",views.a_signup,name="a_signup"),
    path("a_logout",views.a_logout,name="a_logout"),
    path("a_home",views.a_home,name="a_home"),
    path("a_delete",views.a_delete,name="a_delete")

    

]
