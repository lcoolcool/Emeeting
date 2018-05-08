# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from meet.models import *
# Register your models here.


class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_date', 'booking_time', 'room')  # list
    search_fields = ('booking_date',)


admin.site.register(Booking, BookingAdmin)
admin.site.register(MeetingRoom)
admin.site.register(UserInfo)
