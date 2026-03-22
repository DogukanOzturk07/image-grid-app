
import os
import math
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image


class ImageGridApp:
    def __init__(self, root):
        self.root = root
        self.root.title("2-Column Image Combiner")
        self.root.geometry("720x560")
        self.root.resizable(False, False)

        self.image_paths = []

        tk.Label(
            root,
            text="Select up to 20 images and combine them into 2 columns",
            font=("Arial", 14, "bold")
        ).pack(pady=15)

        tk.Label(
            root,
            text="All images will be resized to the same width. Layout: 2 columns, up to 10 rows.",
            font=("Arial", 10)
        ).pack(pady=5)

        tk.Button(
            root,
            text="Select Images",
            font=("Arial", 12),
            width=22,
            command=self.select_images
        ).pack(pady=10)

        tk.Button(
            root,
            text="Clear List",
            font=("Arial", 12),
            width=22,
            command=self.clear_images
        ).pack(pady=5)

        self.listbox = tk.Listbox(root, width=90, height=14)
        self.listbox.pack(pady=15)

        tk.Button(
            root,
            text="Combine and Save",
            font=("Arial", 12, "bold"),
            width=22,
            command=self.combine_images
        ).pack(pady=10)

        self.status_label = tk.Label(
            root,
            text="No images selected.",
            fg="blue",
            font=("Arial", 10)
        )
        self.status_label.pack(pady=10)

    def select_images(self):
        filetypes = [
            ("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp *.tiff"),
            ("All Files", "*.*")
        ]

        selected = filedialog.askopenfilenames(
            title="Select up to 20 images",
            filetypes=filetypes
        )

        if not selected:
            return

        selected = list(selected)[:20]
        self.image_paths = selected

        self.listbox.delete(0, tk.END)
        for idx, path in enumerate(self.image_paths, start=1):
            self.listbox.insert(tk.END, f"{idx}. {os.path.basename(path)}")

        count = len(self.image_paths)
        rows = math.ceil(count / 2)
        self.status_label.config(
            text=f"{count} image(s) selected. Final layout: 2 columns x {rows} row(s)."
        )

        if len(selected) == 20:
            messagebox.showinfo("Limit Applied", "Maximum 20 images were loaded.")

    def clear_images(self):
        self.image_paths = []
        self.listbox.delete(0, tk.END)
        self.status_label.config(text="No images selected.")

    def combine_images(self):
        if not self.image_paths:
            messagebox.showwarning("Warning", "Please select at least 1 image.")
            return

        try:
            images = []
            for path in self.image_paths:
                img = Image.open(path).convert("RGB")
                images.append(img)

            target_width = min(img.width for img in images)

            resized_images = []
            for img in images:
                new_height = int((target_width / img.width) * img.height)
                resized = img.resize((target_width, new_height), Image.LANCZOS)
                resized_images.append(resized)

            rows = []
            for i in range(0, len(resized_images), 2):
                left_img = resized_images[i]
                right_img = resized_images[i + 1] if i + 1 < len(resized_images) else None
                rows.append((left_img, right_img))

            row_heights = []
            for left_img, right_img in rows:
                if right_img is not None:
                    row_heights.append(max(left_img.height, right_img.height))
                else:
                    row_heights.append(left_img.height)

            total_height = sum(row_heights)
            total_width = target_width * 2

            combined_image = Image.new("RGB", (total_width, total_height), "white")

            y_offset = 0
            for row_index, (left_img, right_img) in enumerate(rows):
                row_height = row_heights[row_index]

                left_y = y_offset + (row_height - left_img.height) // 2
                combined_image.paste(left_img, (0, left_y))

                if right_img is not None:
                    right_y = y_offset + (row_height - right_img.height) // 2
                    combined_image.paste(right_img, (target_width, right_y))

                y_offset += row_height

            save_path = filedialog.asksaveasfilename(
                title="Save combined image",
                defaultextension=".jpg",
                filetypes=[
                    ("JPEG Image", "*.jpg"),
                    ("PNG Image", "*.png")
                ]
            )

            if not save_path:
                self.status_label.config(text="Save cancelled.")
                return

            if save_path.lower().endswith(".png"):
                combined_image.save(save_path)
            else:
                combined_image.save(save_path, quality=95)

            self.status_label.config(
                text=f"Saved successfully: {os.path.basename(save_path)}"
            )
            messagebox.showinfo("Success", "Images combined and saved successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageGridApp(root)
    root.mainloop()
