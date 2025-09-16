import streamlit as st
import sqlite3
import qrcode
import io
from PIL import Image

# --- DB Setup ---
conn = sqlite3.connect("lostfound.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        image BLOB,
        qr_code BLOB
    )
''')
conn.commit()

# --- Functions ---
def save_item(name, description, image_data, qr_data):
    c.execute("INSERT INTO items (name, description, image, qr_code) VALUES (?, ?, ?, ?)",
              (name, description, image_data, qr_data))
    conn.commit()

def get_items():
    c.execute("SELECT id, name, description, image, qr_code FROM items")
    return c.fetchall()

# --- Streamlit UI ---
st.title("🎒 Campus Lost & Found Demo")

menu = ["Upload Lost Item", "View Found Items"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Upload Lost Item":
    st.header("📤 Upload Lost Item")
    name = st.text_input("Item Name")
    description = st.text_area("Description")
    uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "png", "jpeg"])

    if st.button("Submit"):
        if name and description and uploaded_file:
            # Save image bytes
            image_bytes = uploaded_file.read()

            # Generate QR code (points to item ID)
            qr = qrcode.QRCode(box_size=8, border=2)
            qr.add_data(f"Item: {name}, Desc: {description}")
            qr.make(fit=True)
            img_qr = qr.make_image(fill="black", back_color="white")

            buf = io.BytesIO()
            img_qr.save(buf, format="PNG")
            qr_bytes = buf.getvalue()

            save_item(name, description, image_bytes, qr_bytes)

            st.success("✅ Item uploaded successfully!")
        else:
            st.error("Please fill all fields and upload an image.")

elif choice == "View Found Items":
    st.header("📋 Found Items List")
    items = get_items()

    if not items:
        st.info("No items uploaded yet.")
    else:
        for item in items:
            st.subheader(item[1])  # name
            st.write(item[2])  # description
            st.image(item[3], caption="Uploaded Image")  # item image
            st.image(item[4], caption="QR Code")  # qr code
            st.markdown("---")
