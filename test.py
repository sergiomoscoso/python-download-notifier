import time

from plyer import notification

print("🔔 Enviando notificación en 3 segundos...")
time.sleep(3)
notification.notify(
    title="✅ Prueba de notificación",
    message="¡Este es un mensaje de prueba!",
    app_name="Notificador de Descargas",
    timeout=5
)
print("📤 Notificación enviada.")
