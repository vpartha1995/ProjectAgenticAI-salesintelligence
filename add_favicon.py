import os, base64

png_b64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAn8B9jYwWwAAAABJRU5ErkJggg=='
static_dir = os.path.join(os.path.dirname(__file__), 'static')
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

path = os.path.join(static_dir, 'favicon.png')
with open(path, 'wb') as f:
    f.write(base64.b64decode(png_b64))

print(f'Wrote placeholder favicon to {path}')