import os

def delete_files_with_pattern(root_folder, pattern):
    for foldername, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            if pattern in filename:
                file_path = os.path.join(foldername, filename)
                try:
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")

# Set the root folder and pattern
root_folder = "D:\\Price mapping files - Onedrive setup"
pattern = "P21"

if __name__ == "__main__":
    # Call the function
    delete_files_with_pattern(root_folder, pattern)