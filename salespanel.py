import streamlit as st
import datetime
from datetime import date, datetime, timedelta
import requests
import json
import pandas as pd
import re
import time
from openai import OpenAI
import tempfile
import altair as alt
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageEnhance, ImageOps
import os
import sys
import io
import numpy as np
import glob
import zipfile

todo_list = '''
- **Media Editor To Do:**

    - [high]integrate the scenic projection creator into the admin panel
    - [medium]add workflow phase and assignee to contact details currently having issues with helper functions
    - [medium]add way to pull up contact in wix from last contacted updater page
    - [medium]kind of confusing that the same email address is used for both last contacted and email gen, maybe they should be their own tabs? Idk its convenient now...
    - [high]add phase and assignee to contact details under outreach page
    - [medium]converter page shows no status updates...
    - [medium]add way to assign new leads to team members. Should change assignee in WIX contact as well as add [Team Member's First Name] to front of contact card.
    - [medium]add way to detect unassigned active leads in the workflow (excluding cold leads/recieved phases)
    - [high]the workflow report that is created needs to be cached so that you don't lose the report when changing tabs... However, clicking on create report again should flush the cache.
    - [high]implement template system that prefils template with customer information, see the example_quote_template variable.
    - [high]image/video compression (may need to create separate backend service for this, current method is slow)
    - [medium]test target size with compression
    - [high]test remove audio (may need to create separate backend service for this, current method is slow)
    - [high]add overlay to video not working (may need to create separate backend service for this, current method is slow)
    - [low]add 3D image functionality
    - [low]test 3D image once implemented
    - [medium]test logo opacity for video
    - [medium]test checkerboard opacity for video
    - [medium]needs to be tested with multiple images
    - [medium]add video display before download (may need to create separate backend service for this, current method is slow)
    - [medium]add smart rename functionality
    - [medium]add super resolution functionality
    - [low]add quality assurance function using machine vision
    - [low]add vision based smart rename
    - [low]implement AI address suggestion based on venue name/website for quote template
    - [low]implement AI suggested delivery and pickup dates for quote template
    - [medium]add text area on email generator page for you to be able to instruct the ai, like telling them that they should ask certain questinos or include other info...

- **General To Do:**

    - [medium]add playfab tools
    - [low]add misc tools like youtube downloader
'''
wix_links_md = """
## **<u>WIX LINKS:</u>**
- [Contacts](https://manage.wix.com/dashboard/64bf18f8-7dd2-412f-8ad3-89311d147a6a/contacts?tab=contacts)
- [Workflow](https://manage.wix.com/dashboard/64bf18f8-7dd2-412f-8ad3-89311d147a6a/workflows/40b525f8-a0ce-4ed7-8366-16cc302f43cb)
- [New Quote](https://manage.wix.com/dashboard/64bf18f8-7dd2-412f-8ad3-89311d147a6a/price-quotes/create)
- [Invoices](https://manage.wix.com/dashboard/64bf18f8-7dd2-412f-8ad3-89311d147a6a/invoices)
- [Inbox](https://manage.wix.com/dashboard/64bf18f8-7dd2-412f-8ad3-89311d147a6a/inbox)
- [Tasks](https://manage.wix.com/dashboard/64bf18f8-7dd2-412f-8ad3-89311d147a6a/tasks)
- [Email Campaigns](https://manage.wix.com/dashboard/64bf18f8-7dd2-412f-8ad3-89311d147a6a/shoutout?referralInfo=sidebar#/dashboard)
"""
slshowtech_links_md = """
## **<u>SLSHOWTECH LINKS:</u>**
- [Homepage](https://www.slshowtech.com/)
- [Shop](https://www.slshowtech.com/shop)
- [Find A Projector](https://www.slshowtech.com/find-a-projector)
- [Scene Library](https://www.slshowtech.com/scenic-projections-library/single-scenes)
- [Community Theatre Connections Discount Program](https://www.slshowtech.com/apply)
- [FAQs](https://www.slshowtech.com/faqs)
- [Feedback Form](https://www.slshowtech.com/feedback)
- [Schedule Call](https://www.slshowtech.com/booking-calendar/new-show-consultation?referral=service_list_widget)
"""
admin_links_md = """
## **<u>ADMIN LINKS:</u>**
- [Shows & Clients](https://drive.google.com/drive/folders/1RX-KHpOGQJveJbPk5k78ij98WGFVTkZX?usp=sharing)
- [3D Animated Show Library Sheet](https://docs.google.com/spreadsheets/d/12FjKOwR_ddgql8l7q91587KfSZyyUREWztwZHZ3E-5Q/edit?usp=sharing)
- [AI Scene Pack Library Sheet](https://docs.google.com/spreadsheets/d/1V6nZQVrGi_Sg410nKIIttGEGFZnhdKgLSTRQQULvxso/edit?usp=drive_link)
- [SLShowTech Developer's Guide](https://docs.google.com/document/d/19X5OOR8yH-fT6x0iOFXSdM34SZlRLwj-aK9zeqaeA-c/edit?usp=sharing)
- [SLShowTech CRM](https://drive.google.com/drive/folders/1V7eA_urgzS4hZ6B0wgjev8KX4gJ2F97t?usp=drive_link)
- [CRM Content Control](https://drive.google.com/drive/folders/1FwvBtsEtR1hBQK8ypBOBD6cFSJ3BoUsm?usp=sharing)
- [Only New Lists](https://drive.google.com/drive/folders/1Yoq0UVw2deh8SIt2vNP2GqnKkQD7XyFd?usp=drive_link)
"""
showone_links_md = """
## **<u>SHOWONE LINKS:</u>**
- [ShowOne](https://www.slshowtech.com/showone)
- [Getting Started](https://www.slshowtech.com/gettingstarted)
- [ShowOne API](https://docs.google.com/spreadsheets/d/1ZfeGbXGVf5EYK77rBlyNMviWNIU4eBFIYGAJmuReUOU/edit?usp=sharing)
"""

email_gen_warning = '''
Before proceeding with the **Generate Email** feature below, please ensure the following steps have been completed:

1. **Enter an Email Address:** Make sure to input the email address in the designated field above.
2. **Press Enter:** After typing the email address, press enter to confirm it.
3. **Paste the Past Conversation:** If dealing with a new lead request or providing context, paste the relevant conversation history into the **past conversation text input area**.
4. **Hit Enter Again:** Ensure that after pasting the conversation, you press enter to finalize the input.

Failure to follow these steps might result in the AI not having the complete context, which could affect the accuracy and relevance of the generated email.
'''

color_key_text = """
- ![#0000FF](https://via.placeholder.com/15/0000FF/0000FF.png) :point_right: Never Contacted
- ![#00FF00](https://via.placeholder.com/15/00FF00/00FF00.png) :point_right: Contacted in the last 7 days
- ![#FFFF00](https://via.placeholder.com/15/FFFF00/FFFF00.png) :point_right: Contacted between 7 and 14 days ago
- ![#FFA500](https://via.placeholder.com/15/FFA500/FFA500.png) :point_right: Contacted between 14 and 30 days ago
- ![#FF0000](https://via.placeholder.com/15/FF0000/FF0000.png) :point_right: Contacted more than 30 days ago
"""

links = [
    {"url": "https://manage.wix.com/dashboard/64bf18f8-7dd2-412f-8ad3-89311d147a6a/contacts?tab=contacts", "label": "Contacts", "icon": "📒", "help": "Goes to Wix contacts"},
    {"url": "https://manage.wix.com/dashboard/64bf18f8-7dd2-412f-8ad3-89311d147a6a/workflows/40b525f8-a0ce-4ed7-8366-16cc302f43cb", "label": "Workflow", "icon": "📑", "help": "Goes to workflow in Wix"},
    {"url": "https://manage.wix.com/dashboard/64bf18f8-7dd2-412f-8ad3-89311d147a6a/price-quotes/create", "label": "New Quote", "icon": "📄", "help": "Creates a new quote in Wix"},
    {"url": "https://manage.wix.com/dashboard/64bf18f8-7dd2-412f-8ad3-89311d147a6a/invoices", "label": "Invoices", "icon": "🧾", "help": "Goes to Wix invoices"},
    {"url": "https://manage.wix.com/dashboard/64bf18f8-7dd2-412f-8ad3-89311d147a6a/inbox", "label": "Inbox", "icon": "📨", "help": "Goes to inbox in Wix"},
    {"url": "https://manage.wix.com/dashboard/64bf18f8-7dd2-412f-8ad3-89311d147a6a/tasks", "label": "Tasks", "icon": "📝", "help": "Goes to tasks in Wix"},
    {"url": "https://docs.google.com/spreadsheets/d/12FjKOwR_ddgql8l7q91587KfSZyyUREWztwZHZ3E-5Q/edit?usp=sharing", "label": "3D Library", "icon": "📚", "help": "Goes to 3D show library in google sheets"},
    {"url": "https://www.slshowtech.com/scenic-projections-library/single-scenes", "label": "AI Scenes", "icon": "🎭", "help": "Browse the scenic projections library"},
    {"url": "https://www.slshowtech.com/find-a-projector", "label": "Projectors", "icon": "📽️", "help": "Shows pricing for projector rentals/purchases and reccomends a projector tailored for a customer's space."},
    {"url": "https://docs.google.com/document/d/19X5OOR8yH-fT6x0iOFXSdM34SZlRLwj-aK9zeqaeA-c/edit?usp=sharing", "label": "Guide", "icon": "📖", "help": "Goes to the developer's guide"},
    {"url": "https://docs.google.com/spreadsheets/d/1ZfeGbXGVf5EYK77rBlyNMviWNIU4eBFIYGAJmuReUOU/edit?usp=sharing", "label": "API", "icon": "🔗", "help": "Access the ShowOne API documentation"}
]


WIX_API_KEY = st.secrets["WIX_API_KEY"]
WIX_ACCOUNT_ID = st.secrets["WIX_ACCOUNT_ID"]
WIX_SITE_ID = st.secrets["WIX_SITE_ID"]

gpt4turbo = 'gpt-4-turbo-preview'
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)

last_sent_campaign_name_override = "'Everything's Coming Up Roses... with SLShowtech 🌹'"
last_sent_campaign_date_override = "3/26/24"

allowed_image_file_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.tiff', '.tif', '.bmp', '.ico', '.webp']
allowed_video_file_extensions = ['.mp4', '.mov', '.avi', '.webm']
allowed_media_file_extensions = allowed_image_file_extensions + allowed_video_file_extensions

is_status_expanded = True


st.set_page_config(
    page_title="SLShowTech Workflow Report",
    page_icon=":performing_arts:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Report a bug': 'https://www.slshowtech.com',
        'Get help': "https://www.slshowtech.com/faqs",
        'About': "# This app is designed to allow a small sales/admin team to more easily manage a business."
    }
)

todays_date = date.today()

slshowtech_info = """AFFORDABLE SCENIC PROJECTIONS FOR THEATRES OF ALL SIZES!

SLSHOWTECH
Transform your stage with ease using our affordable scenic projection packages and comprehensive projector rental packages. Immerse your audience in the magic of theater with our script-accurate & 3D animated scenes.

Our ShowOne app empowers you with the tools to tailor each scene seamlessly to your artistic vision. Reach out to us to discover how you can elevate your next production with just a few clicks!

- Pricing -
Single Scenes(Images): $19* Single Scenes(3D Animated): $99*| Full Show Packages (Images): $199* | Full Show Packages (3D Animated): $350-KIDS, $400-JR/YOUTH, $600-FULL VERSION* 

Projector Rentals (free shipping): $1199*/wk

*Price represents the starting point and may vary based on product features, customization, and options. Additional details available upon request.

FREE 24/7 TECH SUPPORT INCLUDED WITH ALL ORDERS!

AFFORDABLE AND CUSTOM PROJECTIONS FOR ALL!

At SLShowTech, our mission is to produce high quality scenic projections that are affordable for everyone.

With deep roots in the theatre community, we are very conscious of budget restrictions. We realize most theatres do not have the budget to pay thousands for projections for one show, which is why we make our scenic projections available for any show for $600 or less. 

Why Directors Choose Us:

Transform Your Stage with 3D Animated Projections: Our comprehensive full show packages infuse your productions with unparalleled depth, offering dynamic 3D transitions, captivating special effects, and immersive interactivity that brings every scene to life.

Budget-Friendly: While we maintain uncompromised quality, we're dedicated to making our projections affordable.

Script-Accurate: Never compromise on your narrative. Our scenes are meticulously crafted according to the official show scripts, taking any guesswork out of the equation.

Instant Customization: Say goodbye to the restrictive nature of static backdrops. Our ShowOne app allows you to tweak and transform scenes in real-time, allowing you to perfectly align every scene with your creative vision. Since every show is different after all!

​"""

example_quote_template = """
Hi ${First Name},

Thank you for requesting a quote for your upcoming production of ${Show Name}. In order to make sure we have a projector available that fits your needs can you please provide us with the following information?

1. The dimensions (width and height) of the screen you’ll be projecting onto.
2. Desired throw distance from the projector to the screen - and if there’s flexibility here.
3. If the projector will be mounted to a standard pipe.
4. Confirmation on whether your team has experience with hanging lights or projectors.
5. Will a [Enter the Delivery Date] delivery and [Enter the Pickup Date] pickup work for you?
6. Please also confirm the address for delivery/pickup: [Enter the Full Address]

Our projector rentals come with free shipping, standard lens, and mounting hardware included. We also provide free 24/7 tech support to ensure everything runs smoothly. 

Proof of insurance is required, but for most schools or organizations that already have insurance, this is just a phone call.

Looking forward to hearing back from you so we can secure the best projector fit for your production.

Best regards,

"""

logo_opacity_default = 0.3
checkerboard_opacity_default = 0.08
bottom_crop_amount = 16  # This is the amount to crop from the bottom of the image
target_size_kb_default = 2500  # Set your desired target size in KB
overlay_checkboard_path = "overlaycheckboard_4K.png"
overlay_path = "overlay.png"

def display_sorted_todo_list(todo_list):
    # Split the list into sections
    sections = todo_list.strip().split('- **')
    sections = sections[1:]  # Remove initial empty item if any
    
    # Definitions for priorities and colors
    priority_mapping = {'high': 1, 'medium': 2, 'low': 3}
    priority_color = {'high': '#FF6347', 'medium': '#FFD700', 'low': '#90EE90'}
    
    for section in sections:
        # Split the section into title and tasks
        title, *tasks = section.split('\n')
        title = title.strip().replace("*","")
        
        # Parse and sort tasks within the section
        parsed_tasks = []
        for task in tasks:
            if ']' in task:
                priority = task.split(']')[0].split('[')[-1].strip()
                task_description = task.split(']')[-1].strip()
                parsed_tasks.append((priority_mapping[priority], f"<li style='color:{priority_color[priority]}'>{task_description}</li>"))
        
        # Sort tasks by priority
        parsed_tasks.sort()
        
        # Display the sorted tasks under the expander
        with st.expander(f"**{title}**", expanded=True):
            task_list_html = "<ul>" + "".join([task for _, task in parsed_tasks]) + "</ul>"
            st.markdown(task_list_html, unsafe_allow_html=True)

def remove_period_from_extensions(extensions_list):
    return [ext.replace(".", "") for ext in extensions_list]

def compress_image(input_image_file, original_format):
    with st.status("Compressing Image..."):
        quality = 85
        buffer = io.BytesIO()

        # Load the image
        st.write("Loading the image...")
        img = Image.open(input_image_file)
        if img.mode == 'RGBA' and original_format.upper() != 'PNG':
            img = img.convert('RGB')
            st.write("Converted image to RGB.")

        # Adjusting strategy based on format
        if original_format.upper() == 'JPEG':
            adjust_quality = True
        else:
            adjust_quality = False
            compress_level = 9  # Max compression for PNG

        # Compress by adjusting quality or using other methods
        while True:
            buffer.seek(0)
            buffer.truncate(0)

            if adjust_quality:
                img.save(buffer, format=original_format, quality=quality)
            else:
                img.save(buffer, format=original_format, optimize=True, compress_level=compress_level)

            size_kb = len(buffer.getvalue()) / 1024
            st.write(f"Quality/Level: {quality if adjust_quality else compress_level}, Size: {size_kb:.2f} KB")

            if size_kb <= target_size_kb or quality <= 10:
                break
            if size_kb > target_size_kb:
                if adjust_quality:
                    quality -= 5
                else:
                    compress_level = max(0, compress_level - 1)

        buffer.seek(0)
        return buffer.getvalue(), quality if adjust_quality else compress_level




def has_dalle_watermark(image):
    # Define the extended rgb sequence
    extended_color_sequence = [
        (255, 255, 102), (255, 255, 102), (255, 255, 102), (255, 255, 102),
        (255, 255, 102), (255, 255, 102), (255, 255, 102), (255, 255, 102),
        (255, 255, 102), (255, 255, 102), (255, 255, 102), (255, 255, 102),
        (255, 255, 102), (255, 255, 102), (255, 255, 102), (255, 255, 102),
        (66, 255, 255), (66, 255, 255), (66, 255, 255), (66, 255, 255),
        (66, 255, 255), (66, 255, 255), (66, 255, 255), (66, 255, 255),
        (66, 255, 255), (66, 255, 255), (66, 255, 255), (66, 255, 255),
        (66, 255, 255), (66, 255, 255), (66, 255, 255), (66, 255, 255),
        (81, 218, 76), (81, 218, 76), (81, 218, 76), (81, 218, 76),
        (81, 218, 76), (81, 218, 76), (81, 218, 76), (81, 218, 76),
        (81, 218, 76), (81, 218, 76), (81, 218, 76), (81, 218, 76),
        (81, 218, 76), (81, 218, 76), (81, 218, 76), (81, 218, 76),
        (255, 110, 60), (255, 110, 60), (255, 110, 60), (255, 110, 60),
        (255, 110, 60), (255, 110, 60), (255, 110, 60), (255, 110, 60),
        (255, 110, 60), (255, 110, 60), (255, 110, 60), (255, 110, 60),
        (255, 110, 60), (255, 110, 60), (255, 110, 60), (255, 110, 60),
        (60, 70, 255), (60, 70, 255), (60, 70, 255), (60, 70, 255),
        (60, 70, 255), (60, 70, 255), (60, 70, 255), (60, 70, 255),
        (60, 70, 255), (60, 70, 255), (60, 70, 255), (60, 70, 255),
        (60, 70, 255), (60, 70, 255), (60, 70, 255), (60, 70, 255)
    ]

    # Convert the image to a numpy array
    img_array = np.array(image)

    # Get the last row of pixels in the image
    second_last_row = img_array[-2, -len(extended_color_sequence):, :3]  # Adjusted to get the second-to-last row

    # Flatten the row to compare with the color sequence
    second_last_row_flat = [tuple(pixel) for pixel in second_last_row]

    # Compare the second-to-last row to the color sequence
    return second_last_row_flat == extended_color_sequence

def crop_image_from_bottom(image, crop_amount):
    """
    Crops the specified amount from the bottom of the image.

    Parameters:
    - image: PIL.Image object, the original image to be cropped.
    - crop_amount: int, the height in pixels to crop from the bottom of the image.

    Returns:
    - PIL.Image object: The cropped image.
    """
    return image.crop((0, 0, image.width, image.height - crop_amount))

def process_video_file(uploaded_video):
    with st.status("Processing Video File...", expanded=is_status_expanded):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            st.write("Saving the video to binary format...")
            # Temporarily save the uploaded video file in binary mode
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4", mode='wb') as tmpfile:
                tmpfile.write(uploaded_video.read())
                tmp_filename = tmpfile.name

            st.write("Loading the video...")
            # Load the video file from the temporary file path
            video_clip = VideoFileClip(tmp_filename)

            if toggle_value_overlay:
                # Process overlay
                st.write("Adding overlay to the video...")
                overlay_image = ImageClip(overlay_path)
                resized_overlay_image = overlay_image.resize(width=video_clip.size[0] / 3).set_opacity(logo_opacity)
                overlay_position = ((video_clip.size[0] - resized_overlay_image.size[0]) / 2,
                                    (video_clip.size[1] - resized_overlay_image.size[1]) / 2)
                resized_overlay_image = resized_overlay_image.set_duration(video_clip.duration).set_position(overlay_position)
                video_clip = CompositeVideoClip([video_clip, resized_overlay_image])

            if toggle_value_audio:
                st.write("Removing audio from the video...")
                video_clip = video_clip.without_audio()

            # Write to a temporary output file
            st.write("Creating an output file...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_output:
                video_clip.write_videofile(tmp_output.name, codec="libx264", temp_audiofile='temp-audio.m4a', remove_temp=True, audio_codec='aac')
                tmp_output_name = tmp_output.name

            # Read the temporary output file into a BytesIO object
            st.write("Converting the file to bytes...")
            video_io = io.BytesIO()
            with open(tmp_output_name, 'rb') as f_output:
                video_io.write(f_output.read())
            video_io.seek(0)
        except Exception as e:
            st.error(e)

        finally:
            st.write("Removing temporary files...")
            # Ensure all temporary files are removed even if an error occurs
            if 'tmp_filename' in locals():
                os.remove(tmp_filename)
            if 'tmp_output_name' in locals():
                os.remove(tmp_output_name)

        return video_io


def process_dalle_watermark(uploaded_image_file, original_format):
    with st.status("Checking for DALL-E Watermark...", expanded=is_status_expanded):
        # Move to the start of the file in case it's been read elsewhere
        uploaded_image_file.seek(0)
        st.write("Loading the image...")
        # Load the image into PIL
        base_image = Image.open(uploaded_image_file).convert("RGBA")
        
        # Example check for the watermark (you'll need to implement has_dalle_watermark)
        if has_dalle_watermark(base_image):  # Assuming has_dalle_watermark now accepts a PIL image and returns a boolean
            st.write("DALL-E Watermark was detected and removed.")
            base_image = crop_image_from_bottom(base_image, bottom_crop_amount)  # Assuming bottom_crop_amount is defined elsewhere

        else:
            st.write("No DALL-E watermark detected.")

        st.write("Saving the image to bytes...")
        # Instead of saving the modified image back to a file, save it to a BytesIO object
        image_io = io.BytesIO()
        base_image.save(image_io, format=original_format.upper())
        image_io.seek(0)  # Reset the buffer to the start

        return image_io

def add_image_overlay(uploaded_image, original_format):
    with st.status("Processing Image File...", expanded=is_status_expanded):

        try:
            st.write("Converting the image to RGBA...")
            base_image = Image.open(uploaded_image).convert("RGBA")

            if toggle_value_overlay:
                # Add logo overlay
                st.write("Adding the logo overlay to the image...")
                overlay_image = Image.open(overlay_path).convert("RGBA")
                overlay_resized = overlay_image.resize((base_image.width // 3, base_image.height // 3), Image.LANCZOS)
                overlay_alpha = overlay_resized.getchannel('A').point(lambda i: int(i * logo_opacity))
                overlay_with_alpha = overlay_resized.copy()
                overlay_with_alpha.putalpha(overlay_alpha)
                overlay_position = ((base_image.width - overlay_resized.width) // 2, (base_image.height - overlay_resized.height) // 2)
                base_image.paste(overlay_with_alpha, overlay_position, overlay_with_alpha)

                # Add checkerboard overlay
                st.write("Adding the checkerboard overlay to the image...")
                checkerboard_overlay = Image.open(overlay_checkboard_path).convert("RGBA")
                checkerboard_overlay_resized = checkerboard_overlay.resize((base_image.width, base_image.height), Image.LANCZOS)
                checkerboard_alpha = checkerboard_overlay_resized.getchannel('A').point(lambda i: int(i * checkerboard_opacity))
                checkerboard_overlay_with_alpha = checkerboard_overlay_resized.copy()
                checkerboard_overlay_with_alpha.putalpha(checkerboard_alpha)
                base_image.paste(checkerboard_overlay_with_alpha, (0, 0), checkerboard_overlay_with_alpha)

            # Instead of saving to a file, save to a BytesIO object
            st.write("Saving to bytes...")
            output_io = io.BytesIO()
            base_image.save(output_io, format=original_format.upper())
            output_io.seek(0)  # Move to the start of the BytesIO buffer

        except Exception as e:
            st.error(e)

        return output_io


def process_files(uploaded_files):
    if not uploaded_files:
        st.write("No files selected, exiting...")
        return

    processed_files = []  # List to store tuples of processed file bytes and new filenames

    with st.spinner("Processing Media..."):
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            extension = os.path.splitext(file_name)[1].lower()

            if extension in allowed_video_file_extensions:
                # Process video files
                base_name, extension = os.path.splitext(file_name)
                new_file_name = f"{base_name}_processed{extension}"
                video_bytes = process_video_file(uploaded_file)
                processed_files.append((video_bytes, new_file_name))

                if len(uploaded_files) == 1:
                    st.download_button("Download Processed Video", video_bytes, file_name=new_file_name, mime="video/mp4")

            elif extension in allowed_image_file_extensions:
                # Process image files
                base_name, extension = os.path.splitext(file_name)
                image_file_name = f"{base_name}_processed{extension}"
                processed_image_io = process_dalle_watermark(uploaded_file, extension[1:])  # Pass the extension without the dot
                image_bytes = add_image_overlay(processed_image_io, extension[1:])
                processed_files.append((image_bytes, image_file_name))

                st.image(image_bytes, caption=f"Processed Image: {file_name}", use_column_width='auto')

                if toggle_value_compress:
                    # Assuming 'image_bytes' is a BytesIO object from 'add_image_overlay'
                    compressed_image_bytes, _ = compress_image(image_bytes, extension[1:])  # image_bytes is already a BytesIO, pass directly
                    if len(uploaded_files) == 1:
                        st.download_button("Download Compressed Image", compressed_image_bytes, file_name=image_file_name, mime=f"image/{extension[1:]}")
                else:
                    if len(uploaded_files) == 1:
                        st.download_button("Download Sample Image", image_bytes.getvalue(), file_name=image_file_name, mime=f"image/{extension[1:]}")

            else:
                st.error("The format of the uploaded file is not supported.")

        if len(uploaded_files) > 1:
            download_processed_files_as_zip(processed_files, extension[1:])



#START OF FUNCTIONS FOR WORKFLOW REPORT
def make_donut(input_response, input_text, input_color):
    if input_color == 'blue':
        chart_color = ['#29b5e8', '#155F7A']
    elif input_color == 'green':
        chart_color = ['#27AE60', '#12783D']
    elif input_color == 'orange':
        chart_color = ['#F39C12', '#875A12']
    elif input_color == 'red':
        chart_color = ['#E74C3C', '#781F16']
    elif input_color == 'yellow':
        chart_color = ['#F4D03F', '#9A7D0A']
    elif input_color == 'purple':
        chart_color = ['#8E44AD', '#5B2C6F']
    elif input_color == 'pink':
        chart_color = ['#FFC0CB', '#FF69B4']

    source = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100-input_response, input_response]
    })
    source_bg = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100, 0]
    })

    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          #domain=['A', 'B'],
                          domain=[input_text, ''],
                          # range=['#29b5e8', '#155F7A']),  # 31333F
                          range=chart_color),
                      legend=None),
    ).properties(width=130, height=130)

    text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          # domain=['A', 'B'],
                          domain=[input_text, ''],
                          range=chart_color),  # 31333F
                      legend=None),
    ).properties(width=130, height=130)
    return plot_bg + plot + text

def get_WIX_header():
    headers = {
    'Content-Type': 'application/json',
    'Authorization': WIX_API_KEY,
    'wix-account-id': WIX_ACCOUNT_ID,
    'wix-site-id': WIX_SITE_ID,
    }
    return headers

def filter_phases(workflow_data, desired_phases):
    """
    Filter out specific phases from all workflows, skipping unwanted phases.

    :param all_workflows: The JSON data containing all workflows.
    :param desired_phases: A list of phase names that we want to filter.
    :return: A dictionary of lists of cards, keyed by workflow ID, that match the desired phases.
    """
    filtered_cards_by_phase = {phase: [] for phase in desired_phases}

    if 'workflow' in workflow_data:
        actual_workflow = workflow_data['workflow']

        if 'phasesList' in actual_workflow and 'phases' in actual_workflow['phasesList']:
            # Process each phase in the phases list
            for phase in actual_workflow['phasesList']['phases']:
                phase_name = phase.get('info', {}).get('name', '')
                # print(f"Processing phase: {phase_name}")

                if phase_name in desired_phases and 'cardsList' in phase:
                    card_count = len(phase['cardsList']['cards'])
                    filtered_cards_by_phase[phase_name].extend(phase['cardsList']['cards'])
                    # print(f"Found {card_count} cards in phase: {phase_name}")
                else:
                    if phase_name in desired_phases:
                        st.info(f"Phase '{phase_name}' found but no 'cardsList' key present.")
        else:
            st.error("The key 'phasesList' or 'phases' is not present in the actual workflow.")
    else:
        st.error("The key 'workflow' is not present in the provided data.")

    return filtered_cards_by_phase

def truncate_card_name(name, length=80):
    """
    Truncate the card name to a specified length, appending an ellipsis if it exceeds this length.

    :param name: The card name to truncate.
    :param length: The maximum allowed length for the card name.
    :return: The truncated card name with an ellipsis if necessary.
    """
    if len(name) > length:
        return name[:length - 3] + "..."
    else:
        return name

def workflows_report(desired_phases):
    progress_bar = st.progress(0)
    workflows = get_all_workflows()
    first_workflow_id = workflows['workflows'][0]['id']
    workflow_contacts = get_workflow_contacts(first_workflow_id)
    filtered_data = filter_phases(workflow_contacts, desired_phases)
    total_contacts = sum(len(cards) for cards in filtered_data.values())
    cards_with_last_contacted = []
    download_status = st.status("Collecting Leads...", expanded=is_status_expanded)
    with download_status:
        for phase, contacts in filtered_data.items():
            st.write(f"Searching the {phase} phase...")
            progress = 0
            total_steps = len(contacts)
            for i, contact in enumerate(contacts):
                progress = int((i + 1) / total_steps * 100)
                progress_bar.progress(progress)
                card_name = contact['info'].get('name', 'Please add workflow card title in WIX!')
                #card_name = truncate_card_name(card_name)
                contact_id = contact['info']['primaryAttachment']['contactId']
                contact_data = get_contact_by_id(contact_id)
                last_contacted_str = contact_data.get('info', {}).get('extendedFields', {}).get('items', {}).get('custom.last-contacted', '')
                last_contacted = datetime.strptime(last_contacted_str, "%Y-%m-%d").date() if last_contacted_str else None
                first_name = contact_data.get("info", {}).get("name", {}).get("first", "")
                last_name = contact_data.get("info", {}).get("name", {}).get("last", "")
                show_name = contact_data.get('info', {}).get('extendedFields', {}).get('items', {}).get('custom.show-name', 'N/A')
                show_version = contact_data.get('info', {}).get('extendedFields', {}).get('items', {}).get('custom.show-version', 'N/A')
                opening_date = contact_data.get('info', {}).get('extendedFields', {}).get('items', {}).get('custom.show-opening-date', 'N/A')

                # Fetching all email addresses
                emails = contact_data.get('info', {}).get('emails', {}).get('items', [])
                email_addresses = [email.get('email') for email in emails if email.get('email')]
                clean_email_addresses = []
                for email in email_addresses:
                    status = get_subscribe(email)
                    if status != "UNSUBSCRIBED":
                        clean_email_addresses.append(email)
                if len(clean_email_addresses) > 1:
                    email_addresses_str = '\n - '.join(clean_email_addresses)
                    email_addresses_str = '- ' + email_addresses_str
                elif len(clean_email_addresses) == 1:
                    email_addresses_str = clean_email_addresses[0]
                else:
                    email_addresses_str = ''

                #email_addresses_str = clean_email_addresses[0]
                cards_with_last_contacted.append((card_name, phase, first_name, last_name, last_contacted, email_addresses_str, show_name, show_version, opening_date))
            # Don't forget to complete the progress at the end
            progress_bar.progress(100)
    progress_bar.empty()
    download_status.update(label=f"Collected {total_contacts} Contacts.", state="complete", expanded=False)

    # Phase priority mapping
    phase_priority = {'Paid': 1, 'Invoiced': 2, 'Quoted': 3, 'Interested': 4, 'New Leads': 5}

    # Modified sort to prioritize last contacted date, then by phase
    cards_with_last_contacted.sort(key=lambda x: (x[4] is not None, x[4] if x[4] is not None else pd.to_datetime('nat'), phase_priority.get(x[1], float('inf'))))

    return cards_with_last_contacted

def get_all_workflows():

    headers = get_WIX_header() 

    try:
        response = requests.get('https://www.wixapis.com/workflows/v1/workflows', headers=headers)

        # Check the response status code to make sure the request was successful
        if response.status_code != 200:
            add_error(f"Error #{response.status_code}")
            add_error(response.text)
            return None

        # Return the list of workflows
        workflows = response.json()
        return workflows

    except Exception as e:
        add_error(f"Error occurred: {e}")
        return None

def get_subscribe(email):
    email = email.strip()
    if "@" in email:
        pass
    else:
        return None

    headers = get_WIX_header()

    sub_status = {
        "subscription": {
            "email": email
        }
    }

    response = requests.post('https://www.wixapis.com/email-marketing/v1/email-subscriptions', headers=headers, json=sub_status)

    if response.status_code != 200:
        st.error(f"Error #{response.status_code}")
        st.error('Error: An error occurred while loading the subscription.')
        st.error(response.text)
        return

    response_text = json.loads(response.text)
    subscription = response_text['subscription']
    subscription_status = subscription['subscriptionStatus']
        # Check the response status code to make sure the create was successful
    if response.status_code == 200:
        print(f"Subscription for {email} is {subscription_status}.")
        # Delete the original duplicate contacts
        # Only delete if previous create/merge was successful
    return subscription_status

def get_contact_id_from_email(first_email):

    headers = get_WIX_header()

    # Set up the query to find all contacts with the specified name
    json_data = {
        'query': {
            'filter': {
                'info.emails.email': first_email,
            },
            'fieldsets': ['FULL']
        },
    }
    # Send the query to the Wix Contacts API
    response = requests.post('https://www.wixapis.com/contacts/v4/contacts/query', headers=headers, json=json_data)

    # Check the response status code to make sure the request was successful
    if response.status_code != 200:
        st.error(f"Error #{response.status_code} - Unable to retrieve contact.")
        return None

    # Get the list of contacts from the response
    contacts = response.json()['contacts']
    #rint("Venue: {}").format(first_name)
    print("Number of contacts found: {}".format(len(contacts)))  


    # If there are no contacts with the specified name, return an empty list
    if not contacts:
        return None

    if contacts:
        first_contact = contacts[0]
        first_contact_id = first_contact["id"]
        return first_contact_id
    else:
        first_contact = {}
        return None

def get_contact_by_id(contact_id):
    if contact_id and contact_id.strip():
        headers = get_WIX_header()

        # Make a GET request to the /contacts/v4/contacts/{contactId} endpoint
        response = requests.get(
            f'https://www.wixapis.com/contacts/v4/contacts/{contact_id}',
            headers=headers,
        )

        # Check the response status code
        if response.status_code == 200:
            # Parse the response JSON
            data = json.loads(response.text)
            # Return the contact data
            print(f"Contact data retrieved successfully: {data['contact']}")
            return data['contact']
        else:
            # Handle unsuccessful request
            st.error(f"Failed to retrieve contact data. Status code: {response.status_code}")
            return None
    else:
        # Handle case where contact_id is None or empty
        st.error("Invalid contact ID provided.")
        return None

def get_workflow_contacts(workflow_id, cards_per_phase=100, options=None):
    print(f"Looking up contacts for workflow: {workflow_id}")
    # Use the Wix Workflows API to retrieve the workflow information
    headers = get_WIX_header()
   
    params = {"cardsPerPhase": cards_per_phase}
    if options is not None:
        params.update(options)

    try:
        response = requests.get(f'https://www.wixapis.com/workflows/v1/workflows/{workflow_id}', headers=headers, params=params)
   
    except Exception as e:
        return None

    #is_token_alive(response)
    # Check the response status code to make sure the request was successful
    if response.status_code != 200:
        st.error(f'Error #{response.status_code} - Could not retrieve workflow.')
        st.error(response.text)
        return

    # Get the workflow information from the response
    try:
        workflow = response.json()
        return workflow
    except Exception as e:
        return None  

def get_workflow_report(desired_phases):
    # This function might wrap around your existing logic for `workflows_report`
    # Ensure to replace `get_all_workflows` and other necessary calls with their actual implementations
    return workflows_report(desired_phases)

def apply_row_color(s):
    """Apply row color based on 'Last Contacted' date."""
    # Define today's date for comparison
    today = pd.to_datetime("today").date()
    
    # Extract the 'Last Contacted' date from the row
    last_contacted = pd.to_datetime(s['Last Contacted']).date() if pd.notnull(s['Last Contacted']) else None
    
    # Define color conditions similar to your Tkinter GUI logic
    if last_contacted is None:
        return ['background-color: blue'] * len(s)
    elif last_contacted >= today - timedelta(days=7):
        return ['background-color: green'] * len(s)
    elif today - timedelta(days=14) <= last_contacted < today - timedelta(days=7):
        return ['background-color: yellow'] * len(s)
    elif today - timedelta(days=30) <= last_contacted < today - timedelta(days=14):
        return ['background-color: orange'] * len(s)
    else:
        return ['background-color: red'] * len(s)

def display_analytics(df_source):
    df = df_source.copy(deep=True)
    # Convert 'Last Contacted' to datetime for comparison
    df['Last Contacted'] = pd.to_datetime(df['Last Contacted'], errors='coerce')

    # Define today's date for comparison
    today = pd.to_datetime('today').normalize()

    # Calculate analytics
    analytics = {
        'total_contacts': len(df),
        'follow_ups_needed': len(df[df['Last Contacted'] < (today - timedelta(days=10))]),
        # Add more analytics as needed
    }

    # Calculate counts for each 'Phase'
    phase_counts = df['Phase'].value_counts().to_dict()

    # Example: Count specific conditions like nationwide orders
    # Assuming 'Card Name' contains pattern [#123]
    nationwide_count = len(df[df['Card Name'].str.contains(r"\[#\d+\]", regex=True, na=False)])

    fues = (analytics['total_contacts'] - analytics['follow_ups_needed'])/analytics['total_contacts'] * 100

    fues_string = f"{fues: .0f}%"

    # Displaying analytics using columns
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

    with stat_col1:
        st.metric(label=":green[Total Active Leads]", value=analytics['total_contacts'], delta=analytics['total_contacts'], delta_color="normal")

    with stat_col2:
        st.metric(label=":red[Follow Ups Needed (>10 Days)]", value=analytics['follow_ups_needed'], delta=analytics['follow_ups_needed'], delta_color="inverse")

    with stat_col3:
        st.metric(label=":green[Nationwide Orders]", value=nationwide_count, delta=nationwide_count, delta_color="normal")

    with stat_col4:
        st.metric(label="Follow-Up Efficiency Score", value=fues_string, delta=fues_string, delta_color="normal")
        # Calling make_donut function to create the donut chart for FUES
        #donut_chart = make_donut(fues, "Follow-Up Efficiency", "green")

        # Display the donut chart in Streamlit
        #st.altair_chart(donut_chart, use_container_width=True)

    num_phases = len(phase_counts)
    columns_per_row = 8
    num_rows = (num_phases + columns_per_row - 1) // columns_per_row  # Calculate how many rows are needed

    for i in range(num_rows):
        # Calculate start and end index for phases to be displayed in the current row
        start_idx = i * columns_per_row
        end_idx = start_idx + columns_per_row
        # Slice the phases for the current row. Convert items to list for slicing if necessary.
        row_phases = list(phase_counts.items())[start_idx:end_idx]
        
        # Create columns for the current row
        phase_cols = st.columns(columns_per_row)
        
        # Iterate over each phase and its count, along with the corresponding column
        for col, (phase, count) in zip(phase_cols, row_phases):
            with col:
                st.metric(label=phase, value=count)

def normalize_text(text):
    """Normalize text by removing spaces around dashes and converting to uppercase."""
    return text.replace(' - ', '-').replace('-', ' ').upper()


def get_workflow_phase_by_contact_id(contact_id, contacts_data):
    try:
        # Check for the existence of 'phasesList' in the data
        if 'workflow' not in contacts_data or 'phasesList' not in contacts_data['workflow']:
            st.error("No contact data available.")
            st.dataframe(contacts_data)
            return 'Unknown'
        
        # Iterate through each phase in the phasesList
        for phase_info in contacts_data['workflow']['phasesList']['phases']:
            # Get the list of cards in the current phase
            cards_list = phase_info.get('cardsList', {})
            # Iterate through each card
            for card in cards_list.get('cards', []):
                primary_attachment = card['info'].get('primaryAttachment', {})
                # Check if this card's contactId matches the contact_id we are looking for
                if primary_attachment.get('contactId') == contact_id:
                    # Return the phase's name
                    return phase_info['info']['name']

        st.error(f"No contact with ID {contact_id} found.")
        return 'Unknown'
    except Exception as e:
        st.error(f"Error retrieving workflow phase name: {str(e)}")
        return 'Unknown'

def get_assignee_by_contact_id(contact_id, contacts_data):
    try:
        # Check for the existence of 'phasesList' in the data
        if 'workflow' not in contacts_data or 'phasesList' not in contacts_data['workflow']:
            st.error("No contact data available.")
            st.dataframe(contacts_data)
            return 'Unknown'
        
        # Iterate through each phase in the phasesList
        for phase_info in contacts_data['workflow']['phasesList']['phases']:
            # Get the list of cards in the current phase
            cards_list = phase_info.get('cardsList', {})
            # Iterate through each card
            for card in cards_list.get('cards', []):
                primary_attachment = card['info'].get('primaryAttachment', {})
                # Check if this card's contactId matches the contact_id we are looking for
                if primary_attachment.get('contactId') == contact_id:
                    card_name = card['info'].get('name', '')
                    # Extract content within brackets for assignee names
                    bracket_contents = re.findall(r'\[(.*?)\]', card_name)
                    return bracket_contents[0] if bracket_contents else 'Unknown'

        st.error(f"No assignee found for contact ID {contact_id}.")
        return 'Unknown'
    except Exception as e:
        st.error(f"Error retrieving assignee: {str(e)}")
        return 'Unknown'

def fetch_contact_details(email):
    contact_id = get_contact_id_from_email(email)
    if not contact_id:
        st.error(f"Unable to fetch contact details for {email}")
        return None

    contact_data = get_contact_by_id(contact_id)
    if 'info' in contact_data:
        first_name = contact_data['info'].get('name', {}).get('first', 'N/A')
        last_name = contact_data['info'].get('name', {}).get('last', 'N/A')
        last_contacted_str = contact_data['info'].get('extendedFields', {}).get('items', {}).get('custom.last-contacted', '')
        last_contacted_date = datetime.strptime(last_contacted_str, "%Y-%m-%d").date() if last_contacted_str else "Never"
        show_name = contact_data['info'].get('extendedFields', {}).get('items', {}).get('custom.show-name', 'N/A')
        show_version = contact_data['info'].get('extendedFields', {}).get('items', {}).get('custom.show-version', 'N/A')
        
        workflows = get_all_workflows()
        first_workflow_id = workflows['workflows'][0]['id']
        workflow_contacts = get_workflow_contacts(first_workflow_id)
        workflow_phase = get_workflow_phase_by_contact_id(contact_id, workflow_contacts)
        assignee = get_assignee_by_contact_id(contact_id, workflow_contacts)

        return {
            "first_name": first_name,
            "last_name": last_name,
            "last_contacted_date": last_contacted_date,
            "show_name": show_name,
            "show_version": show_version,
            "workflow_phase": workflow_phase,
            "assignee": assignee
        }
    else:
        st.error("Invalid contact data structure")
        return None


def get_contact_revision(contact_ID):
    if (contact_ID is not None) and (contact_ID!=""):
        headers = get_WIX_header()

        # Make a GET request to the /contacts/v4/contacts/{contactId} endpoint
        response = requests.get(
            'https://www.wixapis.com/contacts/v4/contacts/' + contact_ID,
            headers=headers,
        )
        # Check the response status code
        if response.status_code == 200:
            # Parse the response JSON
            data = json.loads(response.text)
            # Return the revision number of the contact
            revision = data['contact']['revision']
            print(f"Current contact revision is: {revision}")

            return revision
        else:
            # Return None if the request was unsuccessful
            st.error("No Revision Was Found!")
            return None
    else:
        # Return None if the request was unsuccessful
        st.error("No Revision Was Found!")
        return None

def get_last_contacted_by_contact_id(contact_id):
    try:
        print("Looking up last contacted date...")
        headers = get_WIX_header()

        # Set up the query to find the contact with the specified contact ID
        json_data = {
            'query': {
                'filter': {
                    'id': contact_id,
                },
                'fieldsets': ['FULL']
            },
        }

        # Send the query to the Wix Contacts API
        response = requests.post('https://www.wixapis.com/contacts/v4/contacts/query', headers=headers, json=json_data)

        # Check the response status code to make sure the request was successful
        if response.status_code != 200:
            st.error(f"Error #{response.status_code} : Unable to retrieve contact.")
            st.error(response.text)
            raise ValueError(f"Error #{response.status_code} : Unable to retrieve contact. {response.text}")
        
        # Get the list of contacts from the response
        contacts = response.json()['contacts']
        print("Number of contacts found: {}".format(len(contacts)))  

        # If there are no contacts with the specified ID, return an error
        if not contacts:
            st.error('No Contact Found')
            last_contacted_date = "Contact Does Not Exist!"
        else:
            # There should be only one contact with the specified ID, so we can directly access it
            first_contact = contacts[0]
            last_contacted_date = first_contact['info']['extendedFields']['items'].get('custom.last-contacted',"")

        return last_contacted_date

    except ValueError as e:
        st.error('Error! - {str(e)}')
        return None

def get_last_sent_campaign_date():
    url = "https://www.wixapis.com/email-marketing/v1/campaigns"
    params = {
        "optionIncludeStatistics": "false",  # Adjust based on your needs
        "visibilityStatuses": "PUBLISHED",  # Assuming "PUBLISHED" means sent and not a draft
        # Add any other parameters you need
    }
    headers = get_WIX_header()

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # This will raise an exception for HTTP error codes
        campaigns = response.json().get('campaigns', [])
        print(campaigns)
        for campaign in campaigns:
            if campaign.get('visibilityStatus') != 'DRAFT':
                # Assuming 'dateUpdated' is the send date; adjust if it's different
                return campaign.get('dateUpdated')
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching campaigns: {e}")
        return None

def update_last_contacted(contact_ID, email, date):
    headers = get_WIX_header()

    # Retrieve the revision number of the contact
    revision = get_contact_revision(contact_ID)

    # Check if the revision number was retrieved successfully
    if revision is not None:
        # Build the request payload with the revision number and the updated "Last Contacted" field
        json_data = {
            'revision': revision,  # The revision number of the contact
            'info' : {
                'extendedFields': {
                    'items': {
                        'custom.last-contacted': date,
                    },
                }
            }    
        }

        # Make a PATCH request to the /contacts/v4/contacts/{contactId} endpoint
        response = requests.patch(
            'https://www.wixapis.com/contacts/v4/contacts/' + contact_ID,
            headers=headers,
            json=json_data,
        )

        # Check the response status code
        if response.status_code == 200:
            # Parse the response JSON
            data = json.loads(response.text)
            # Return the revision number of the contact
            revision = data['contact']['revision']
            st.success(f'The last contacted date for {email} was updated to {date}.')
            st.balloons()

        else:
            # Return None if the request was unsuccessful
            st.error("Error updating last contacted date!")
    else:
        st.error(f"Unable to find the revision for {email}.")
        #add_error("Error",'Error: Unable to retrieve revision number')

def generate_response_email(prompt):
    """
    Generates a response email using GPT-4 Turbo.
    """
    user_message = {
        "role": "user",
        "content": prompt
    }

    try:
        completion = client.chat.completions.create(
            model=gpt4turbo,
            messages=[user_message]
        )
        response_email = completion.choices[0].message.content
        return response_email
    except Exception as e:
        st.error(e)
        return "There was an error generating this email. Please try again."

def generate_email_prompt(first_name, last_name, last_contacted_date, show_name, show_version, past_conversation):
    prompt = f'Company Info: {slshowtech_info} //! Past Conversation: {past_conversation} !// ---Generate a professional and engaging email for a theatre or theatre director named {first_name + " " + last_name} who has previously shown interest in our scenic projections. The last communication was on {last_contacted_date} and todays date is {todays_date}. The show they are interested in is {show_name}, particularly the {show_version} version. Our affordable projector rentals offer theatres a chance to bring high quality gear into their theatres starting at $1199/wk. Our scenic projections offer immersive 3D animated scenes, script accuracy, and are affordable. Our ShowOne app allows for instant scene customization and we also offer up to 10 hours of edits on the house with each purchase to ensure the projections are customized to your show. We are committed to quality while keeping our projections affordable. ***If show name is N/A, please dont refer to a show as they may not have one planned yet.*** No need for language like I hope this message finds you well or other fluff, try to be straight to the point. ***KEEP IT SHORT AND SWEET!*** Especially if it is just a follow up. ***DO NOT BE OVER THE TOP*** Be very down to earth and approachable. ***DO NOT REPEAT INFORMATION, MAKE SURE TO TAKE INTO CONSIDERATION THE ENTIRE CONVERSATION. DO NOT ALWAYS PUSH THE SHOWONE APP, OUR SCENIC PROJECTIONS, OR PROJECTOR RENTALS WITHOUT PRIOR CONTEXT THAT THE CUSTOMER ACTUALLY WANTS THAT. ALSO PLEASE DO NOT CONFUSE PROJECTOR RENTALS WITH PROJECTOR PURCHASES, CHECK THE PRIOR CONVERSATION FOR CONTEXT! !!PLEASE TAILOR THE EMAIL TO THE CUSTOMERS NEEDS!!***'    
    return prompt

def adjust_filename(file_name):
    # Correctly handle file names with multiple dots
    base_name = os.path.splitext(file_name)[0]
    # Shorten the base name if it's too long
    if len(base_name) > 100:
        base_name = base_name[:100]
    return base_name

def download_single_image_and_convert_to_png(uploaded_file):
    file_name, file_extension = os.path.splitext(uploaded_file.name.lower())
    
    if file_extension in allowed_image_file_extensions:
        img = Image.open(uploaded_file)
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        adjusted_filename = f"{adjust_filename(uploaded_file.name)}.png"
        mime_type = "image/png"
        buffer_value = img_buffer.getvalue()
    elif file_extension in allowed_video_file_extensions:
        # Use a temporary file if necessary for video processing
        video = VideoFileClip(uploaded_file.temporary_file_path() if hasattr(uploaded_file, 'temporary_file_path') else uploaded_file)
        video_buffer = io.BytesIO()
        video.write_videofile(video_buffer, codec="libx264", audio_codec="aac")
        video_buffer.seek(0)
        
        adjusted_filename = f"{adjust_filename(uploaded_file.name)}.mp4"
        mime_type = "video/mp4"
        buffer_value = video_buffer.getvalue()
    else:
        raise ValueError("Unsupported file type.")

    st.download_button(f"Download Converted {file_extension.upper()[1:]}",
                       buffer_value,
                       file_name=adjusted_filename,
                       mime=mime_type)

def download_multiple_images_as_zip_and_convert_to_png(uploaded_files):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for uploaded_file in uploaded_files:
            file_extension = os.path.splitext(uploaded_file.name.lower())[1]
            if file_extension in allowed_image_file_extensions:
                img = Image.open(uploaded_file)
                img_png_buffer = io.BytesIO()
                img.save(img_png_buffer, format='PNG')
                img_png_buffer.seek(0)
                filename = f"{adjust_filename(uploaded_file.name)}.png"
                zip_file.writestr(filename, img_png_buffer.getvalue())
            elif file_extension in allowed_video_file_extensions:
                # Use a temporary file if necessary for video processing
                video = VideoFileClip(uploaded_file.temporary_file_path() if hasattr(uploaded_file, 'temporary_file_path') else uploaded_file)
                video_buffer = io.BytesIO()
                video.write_videofile(video_buffer, codec="libx264", audio_codec="aac")
                video_buffer.seek(0)
                filename = f"{adjust_filename(uploaded_file.name)}.mp4"
                zip_file.writestr(filename, video_buffer.getvalue())
            else:
                raise ValueError("Unsupported file type.")
    zip_buffer.seek(0)
    st.download_button("Download Converted Files as ZIP",
                       zip_buffer.getvalue(),
                       file_name="converted_files.zip",
                       mime="application/zip")

def download_processed_files_as_zip(processed_files):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_bytes, file_name in processed_files:
            zip_file.writestr(file_name, file_bytes.getvalue())  # Write the already processed file bytes to the zip

    zip_buffer.seek(0)
    st.download_button("Download All Processed Files as ZIP",
                       zip_buffer.getvalue(),
                       file_name="processed_files.zip",
                       mime="application/zip")

def convert_images_to_png_and_zip(uploaded_files):
    if uploaded_files:
        if len(uploaded_files) == 1:
            # Handle the single file case
            uploaded_file = uploaded_files[0]
            file_extension = os.path.splitext(uploaded_file.name.lower())[1]
            original_format = file_extension[1:].upper()  # This skips the dot and converts the rest to uppercase
            download_single_image_and_convert_to_png(uploaded_file)
            
        else:
            download_multiple_images_as_zip_and_convert_to_png(uploaded_files)
    else:
        st.write("No files uploaded.")

# Step 1: Modify the DataFrame to include hyperlinks
# Define the function to create a hyperlink for each email
def format_email(email):
    # Assuming email is a string. If it's a list of emails, you'll need additional handling
    links = []
    for e in email.split(" - "):  # Adjusting for your multiple emails split by " - "
        links.append(f'<a href="?tab=Outreach&email={e.strip()}" target="_self">{e}</a>')
    return " - ".join(links)

def display_report():
    st.header("💡 Report Creator")

    # Existing phase selection
    desired_phases = st.multiselect("Filter by Phase", options=["Cold Leads", "New Leads", "Interested", "Quoted", "Invoiced", "Paid", "Received Show"], default=["New Leads", "Interested", "Quoted", "Invoiced", "Paid"], key="selected_phase")

    # Team Member selection
    selected_team_members = st.multiselect("Filter by Team Member", options=["Diane", "Nick", "Nicole"], default=[], key="selected_team_member")

    # Nationwide Only checkbox
    nationwide_only = st.checkbox("Filter by Nationwide Only", key="nationwide_only")

    # Button to generate report
    if st.button("Generate Report"):
        if not desired_phases:
            st.warning("Please select at least one phase.")
        else:
            # Assuming get_workflow_report already fetches the necessary data
            st.session_state.report_data = get_workflow_report(desired_phases)
            st.divider()
            # Filter by team member if any are selected
            if selected_team_members:
                # Assuming report_data is a list of rows and selected_team_members is a list of team member names.
                normalized_team_members = [normalize_text(member) for member in selected_team_members]

                filtered_report_data = []
                for row in st.session_state.report_data:
                    # Extract text within brackets
                    bracket_contents = re.findall(r'\[(.*?)\]', row[0])
                    normalized_bracket_contents = [normalize_text(content) for content in bracket_contents]
                    
                    # Check if any normalized team member name is in the normalized bracket contents
                    if any(member in content for member in normalized_team_members for content in normalized_bracket_contents):
                        filtered_report_data.append(row)

                st.session_state.report_data = filtered_report_data
            
            # Filter for Nationwide only if checkbox is checked
            if nationwide_only:
                nationwide_pattern = re.compile(r"\[#\d+\]")  # Regex to match [#123456] patterns
                st.session_state.report_data = [row for row in st.session_state.report_data if nationwide_pattern.search(row[0])]


    st.write(f"{st.session_state=}")       
    if st.session_state.report_data:
        # Define the column names for the DataFrame
        column_names = ['Card Name', 'Phase', 'First Name', 'Last Name', 'Last Contacted', 'Email Addresses', 'Show Name', 'Show Version', 'Opening Date']
        
        # Convert report_data to a DataFrame
        df = pd.DataFrame(st.session_state.report_data, columns=column_names)
        # Apply the styling
        df['Email Addresses'] = df['Email Addresses'].apply(format_email)
        df_styled = df.style.apply(apply_row_color, axis=1)
        
        # Display the DataFrame
        st.header("Analytics")
        display_analytics(df)
        st.divider()
        st.header("Detailed View")
        

        # Display the DataFrame as HTML
        st.markdown(df_styled.to_html(escape=False), unsafe_allow_html=True)
        #st.dataframe(df_styled, hide_index=True)
        st.divider()
            # Display a color key for the DataFrame styling
        st.header("Color Key")
        st.write(color_key_text, unsafe_allow_html=False)

    else:
        st.warning("No contacts were found that matched the filters.")

def display_outreach(email=""):
    last_contacted_container = st.container()
    with last_contacted_container:
        st.header("⚡ Last Contacted Updater")
        email = st.text_input("Email Address:", value=email)
        st.write("Contact Details:")
        
        # Create a placeholder for contact details
        contact_details_placeholder = st.empty()
        
        # Function to display contact details
        def display_contact_details(details):
            if details:
                # Clear the previous content
                contact_details_placeholder.empty()
                with contact_details_placeholder.container():
                    # Create a DataFrame from the details dictionary
                    df = pd.DataFrame([details])
                    # Automatically use the dictionary keys as column headers and capitalize them
                    df.columns = [col.replace('_', ' ').title() for col in df.columns]
                    # Display the DataFrame without index
                    st.dataframe(df, hide_index=True)
            else:
                contact_details_placeholder.error("Contact details not found.")



        
        contact_details = {}
        if email:
            contact_details = fetch_contact_details(email)
            display_contact_details(contact_details)
        selected_date = st.date_input(
            "Choose A New Last Contacted Date:", 
            value=date.today(),
            format="MM/DD/YYYY",
            help="Choose the date you last contacted the client. You can set this date into the future if the client needs a break from communications."
        )
        
        def update_and_refresh_contact_details(contact_id, new_date):
            # Update the last contacted date in the backend
            update_last_contacted(contact_id, email, new_date)
            # Refresh the contact details to reflect the update
            return fetch_contact_details(email)
        
        # Inside your button actions after updating contact details
        if st.button("Update Last Contacted", help="This will update the last contacted date for the contact that belongs to this email to the chosen date (defaults to today)."):
            if email:
                contact_id_to_update = get_contact_id_from_email(email)
                formatted_date = selected_date.isoformat()
                contact_details = update_and_refresh_contact_details(contact_id_to_update, formatted_date)
                if contact_details:
                    display_contact_details(contact_details)  # Refresh the displayed contact details
                else:
                    st.error("Failed to update contact details. Please try again.")
            else:
                st.error("Please enter an email first and try again.")
        # Button to snooze for 6 months with help text
        if st.button("Snooze 6 Months", help="Postpone the follow-up action for this contact by 6 months. This will update the last contacted date to 6 months from today."):
            if email:
                contact_id_to_update = get_contact_id_from_email(email)
                snooze_date = (date.today() + timedelta(days=182)).isoformat()  # Approximately 6 months
                contact_details = update_and_refresh_contact_details(contact_id_to_update, snooze_date)
                if contact_details:
                    display_contact_details(contact_details)  # Refresh the displayed contact details
                else:
                    st.error("Failed to update contact details. Please try again.")
            else:
                st.error("Please enter an email first and try again.")

        # Button to snooze for 1 year with help text
        if st.button("Snooze 1 Year", help="Postpone the follow-up action for this contact by 1 year. This will update the last contacted date to 1 year from today."):
            if email:
                contact_id_to_update = get_contact_id_from_email(email)
                snooze_date = (date.today() + timedelta(days=365)).isoformat()  # 1 year
                contact_details = update_and_refresh_contact_details(contact_id_to_update, snooze_date)
                if contact_details:
                    display_contact_details(contact_details)  # Refresh the displayed contact details
                else:
                    st.error("Failed to update contact details. Please try again.")
            else:
                st.error("Please enter an email first and try again.")

        st.divider()
    st.header("⚠️ Important Warning ⚠️")
    st.markdown(email_gen_warning)
    st.divider()
    st.header("💌 Email Generator")
    past_conversation = st.text_area("Past Conversation:", "", height=300)
    response_email = ""
    if st.button("Generate Email"):
        with st.spinner('Generating your email, please wait...'):
            if email:
                if contact_details:
                    contact_details['past_conversation'] = past_conversation.strip()  # Using strip() to remove any leading/trailing whitespace
                    prompt = generate_email_prompt(**contact_details)
                    response_email = generate_response_email(prompt)
                else:
                    st.error("Unable to fetch contact details.")
            else:
                st.error("Email not found, please try again.")

            if response_email != "":
                st.divider()
                st.text_area("Suggested Email:", response_email, height=400)



def display_email_campaigns():
    with st.container(border=True):
        st.page_link("https://manage.wix.com/dashboard/64bf18f8-7dd2-412f-8ad3-89311d147a6a/shoutout?referralInfo=sidebar#/dashboard", label=" All Campaigns", icon="📫", help="Takes you to our email campaign manager in WIX.")
    st.header("Last Sent Campaign:")
    #last_sent_campaign_name, last_sent_campaign_date = get_last_sent_campaign_date()   
    st.text(f"{last_sent_campaign_name_override} was sent out on {last_sent_campaign_date_override}.")

def display_media_editor():
    #START OF STREAMLIT USER INTERFACE
    st.header("🎞️ Media Editor (video not yet supported)")

    #FILE UPLOADER
    uploaded_files = st.file_uploader("Choose a media file", accept_multiple_files=True,type=remove_period_from_extensions(allowed_media_file_extensions))

    #IMAGE SECTION

    #SETTING CONTAINER
    with st.expander("Settings"):

    #GENERAL SETTINGS
        st.header("General")
        with st.container(height=None,border=True):
            toggle_value_overlay_key = "toggle__value_overlay_key"
            with st.container(height=None,border=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write("Add Overlay")
                with col2:
                    toggle_value_overlay = st.toggle("",key=toggle_value_overlay_key,value=True)
            with st.container(height=None,border=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write("Logo Opacity")
                with col2:
                    logo_opacity = st.slider("",0.00,1.00,logo_opacity_default)
            with st.container(height=None,border=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write("Checkerboard Opacity")
                with col2:
                    checkerboard_opacity = st.slider("",0.00,0.20,checkerboard_opacity_default)



    #OUTERMOST CONTAINER
        st.header("📷 Image Settings")
        with st.container(height=None,border=True):

            #unique key for the image settings
           
            toggle_value_3d_image_key = "toggle_value_3d_image_key"
            toggle_value_compress_key = "toggle_value_compress_key"
            #unique key for video settings
            toggle_value_audio_key = "toggle_value_audio_key"
            
    #SMALLER CONTAINERS
            
            with st.container(height=None,border=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write("3D Image")
                with col2:
                    toggle_value_3d_image = st.toggle("",key=toggle_value_3d_image_key,value=False)
            with st.container(height=None,border=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write("Compress Image")
                with col2:
                    toggle_value_compress = st.toggle("",key=toggle_value_compress_key,value=False)
            with st.container(height=None,border=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write("Target Size (kb)")
                with col2:
                    target_size_kb = st.slider("",1000,10000,target_size_kb_default)

        #VIDEO SECTION
        st.header("🎬 Video Settings")
        #OUTERMOST CONTAINER
        with st.container(height=None,border=True):
        #INNER CONTAINER
            with st.container(height=None,border=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write("Remove Audio")
                with col2:
                    toggle_value_audio = st.toggle("",key=toggle_value_audio_key,value=False)

#IMAGE PREVIEW AND VIDEO PREVIEW 

    st.subheader('', divider='rainbow')
    #CREATE BUTTON
    if uploaded_files:
        if st.button("**CREATE**", key=None, help=None, on_click=None, args=None, kwargs=None, type="secondary", disabled=False, use_container_width=True):
            process_files(uploaded_files)

def display_converters():
    # Streamlit UI part
    st.header('🔄 Convert Any Image to PNG')
    uploaded_files = st.file_uploader(
        "Upload image files",
        type=remove_period_from_extensions(allowed_image_file_extensions),
        accept_multiple_files=True
    )
    if st.button('Convert'):
        convert_images_to_png_and_zip(uploaded_files)

def display_all_links():

    # Markdown with categorized links
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        with st.container(height=None, border=True):
            st.markdown(wix_links_md, unsafe_allow_html=True) 
    with col2:
        with st.container(height=None, border=True):
            st.markdown(slshowtech_links_md, unsafe_allow_html=True) 
    with col3:
        with st.container(height=None, border=True):
            st.markdown(admin_links_md, unsafe_allow_html=True)
    with col4:
        with st.container(height=None, border=True):
            st.markdown(showone_links_md, unsafe_allow_html=True) 

def display_release_notes():
    display_sorted_todo_list(todo_list)

##########START OF STREAMLIT UI##########

# Initialization
if 'report_data' not in st.session_state:
    st.info("Initializing Report Data!")
    st.session_state.report_data = []

st.title(":performing_arts: SLShowTech Admin Panel :performing_arts:")
st.write("          ")
# Define a list of dictionaries, each representing a page link with its details

with st.container(height=None, border=True):
    # Create the same number of columns as there are links
    cols = st.columns(len(links))
    # Loop over each column and corresponding link details
    for col, link in zip(cols, links):
        with col:
            st.page_link(link["url"], label=link["label"], icon=link["icon"], help=link["help"])
# Define the tabs and their corresponding names
tab_names = ["All Links", "Report", "Outreach", "Email Campaigns", "Media Editor", "Converters", "Release Notes"]
tab_functions = [display_all_links, display_report, display_outreach, display_email_campaigns, display_media_editor, display_converters, display_release_notes]

# Access current query parameters
current_params = st.query_params

# Attempt to get the default tab from the query params or use "Report" as fallback
default_tab = current_params.get('tab', "Report")
default_index = tab_names.index(default_tab)

# Selectbox for choosing the tab, setting default based on URL query parameters
selected_tab = st.selectbox("Current Page:", tab_names, index=default_index)

# Directly update the 'tab' parameter in query_params
current_params['tab'] = [selected_tab]
st.query_params = current_params

# Call the function associated with the selected tab
selected_index = tab_names.index(selected_tab)
if selected_tab == "Outreach" and 'email' in current_params:
    # Assuming your display_outreach function can accept an email to pre-fill
    tab_functions[selected_index](current_params['email'])
else:
    tab_functions[selected_index]()
