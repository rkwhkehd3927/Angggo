# Generated by Django 5.1.4 on 2025-01-11 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0010_alter_board_bselect'),
    ]

    operations = [
        migrations.AlterField(
            model_name='board',
            name='bselect',
            field=models.CharField(choices=[('풍경', '풍경🌴'), ('감성카페', '감성카페☕'), ('교통', '교통🚗'), ('실시간공유', '실시간공유🗫'), ('추천맛집', '추천맛집😋'), ('웨이팅', '웨이팅👥'), ('취미', '취미🎮'), ('사건사고', '사건사고😈'), ('생활/편의', '생활/편의🧼'), ('기타', '기타🔍')], max_length=500),
        ),
    ]
