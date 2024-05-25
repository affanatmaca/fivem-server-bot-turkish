# FiveM Sunucu Botu

Bu, `discord.py` kütüphanesini kullanarak Python ile yazılmış bir Discord botudur. Bot, üyelerin bilet oluşturmasına, yönetmesine ve kapatmasına olanak tanıyan bir bilet sistemi sağlar. Bu bot ayrıca emojiler, mesajlar ve ses kanalı etkinlikleri için çeşitli kayıt işlevleri içerir, özellikle FiveM sunucu toplulukları için uyarlanmıştır.

## Özellikler

- Bilet oluşturma ve yönetme
- Emoji kullanımını kaydetme
- Mesaj ve kanal etkinliklerini kaydetme
- Üye rolleri ve onaylarını yönetme
- Yeni kayıtlar ve destek istekleri hakkında yetkililere bildirimde bulunma

## Gereksinimler

- Python 3.8 veya üzeri
- `discord.py` kütüphanesi
- `python-dotenv` kütüphanesi

## Kurulum

1. Depoyu klonlayın:
    ```bash
    git clone https://github.com/affanatmaca/fivem-server-bot.git
    cd fivem-server-bot
    ```

2. Gerekli paketleri yükleyin:
    ```bash
    pip install discord.py python-dotenv
    ```

3. Proje dizininde bir `.env` dosyası oluşturun ve Discord bot tokeninizi ekleyin:
    ```
    DISCORD_BOT_TOKEN=bot-tokeniniz
    ```

4. `main.py` dosyasını sunucu ve kanal ID'lerinizle güncelleyin.

## Kullanım

Botu çalıştırmak için:
```bash
python main.py
```

Bu proje tamamamen türkçedir inglizce projeye bakmak istiyorsanız linki kontrol edin https://github.com/affanatmaca/fivem-server-bot/
