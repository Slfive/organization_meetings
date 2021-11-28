"""Here is DataBase"""

from django.db import models

class VK_sender(models.Model):
    """Table for users messages"""

    user_id = models.TextField(max_length=100, blank=True)
    coor_x = models.TextField(blank=True)
    coor_y = models.TextField(blank=True)
    text = models.TextField(blank=True)
    key_phrase = models.TextField(blank=True)
    type = models.IntegerField()
    count = models.IntegerField()
