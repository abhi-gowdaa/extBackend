from fastapi import FastAPI, HTTPException 
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
import requests
from bs4 import BeautifulSoup
import validators
from youtube_transcript_api import YouTubeTranscriptApi

from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI()

origins=[
    "http://localhost:3000",
    "chrome-extension://mjdggpghaabiocpngdkageeenpmgebim"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

model=genai.GenerativeModel("gemini-pro")


prompt1="""
As a Web Insight Summarizer, your task is to summarize the given web 
content into a clear and informative text of around 250 words. 
Highlight key points using bullet points or numbered lists to emphasize important details. 
Keep the summary objective, coherent, and focused on the main insights without adding personal opinions.
Here's an example:

Main Topic: Climate Change
-Rising Temperatures: Due to greenhouse gas emissions.
-Consequences: Extreme weather events, rising sea levels, loss of biodiversity.
-Mitigation Strategies: Renewable energy, carbon reduction, sustainable practices.
-Call to Action: Urgent collective action needed.
Your summary should provide a comprehensive overview of the content, enabling readers to grasp the main insights efficiently.
Remember to keep the summary objective and focused on the key points of the content without adding unnecessary details or opinions. 
Providing a clear and digestible overview will help users grasp the main insights from the parsed HTML content efficiently which is given in the following content        :
"""

prompt2="""
As an Insight Summarizer, your task is to distill provided information into a concise and informative 
summary of around 250 words. Utilize bullet points or numbered lists to highlight key
 points and ensure clarity and coherence in your summary. Avoid injecting personal
opinions and focus solely on presenting the main insights from the content.
 Here's an example:

Main Topic: [Main topic of the content]
[Key point 1]: [Description or detail]<br>
[Key point 2]: [Description or detail]
[Key point 3]: [Description or detail]
<br>
Additional Considerations:
[Additional consideration 1]: [Description or detail]
[Additional consideration 2]: [Description or detail]
[Additional consideration 3]: [Description or detail]

Your summary should provide a comprehensive overview of the content, enabling readers to understand the main
 insights efficiently. Remember to maintain objectivity and focus on the key points to ensure 
 clarity and usefulness for the reader     
"""

prompt6="""
As an Insight Summarizer, your task is to distill provided information into a concise and informative 
summary of around 250 words. Utilize bullet points or numbered lists to highlight key
 points and ensure clarity and coherence in your summary. Avoid injecting personal
opinions and focus solely on presenting the main insights from the content.
Ensure to structure the content using HTML tags like <p> for paragraphs and<ul>, <li> for list items. heading <b> tag , next line <br>  , dont use "\n" , instead use <br> instead for next line
 Here's an structure of output:
<p><b>Main Topic:[Main topic of the content]<b><br><ul><li>[Key point 1]: [Description or detail]</li><li>[Key point 2]: [Description or detail]</li><li>[Key point 3]: [Description or detail]</li></ul><br><b>Additional Considerations:<b><br><ul><li>[Additional consideration 1]: [Description or detail]</li><li>[Additional consideration 2]: [Description or detail]</li><li>[Additional consideration 3]: [Description or detail]</li></ul></p>

Your summary should provide a comprehensive overview of the content, enabling readers to understand the main insights efficiently. Remember to maintain objectivity and focus on the key points to ensure clarity and usefulness for the reader."

Example:
<p><b>Main Topic: FastAPI - A Quick Overview</b></p><p>FastAPI makes it quicker and easier to develop APIs with Python. In this course, Tommy will guide you through his first API Crash Course, demonstrating how FastAPI works.</p><p>FastAPI is a modern, fast, and high-performance web framework for building APIs with Python. It offers a straightforward approach to developing web applications.</p><p>Here are some key points to remember:</p><ul><li>FastAPI is easy to install using the Python package manager, Pip.</li><li>Ensure you have Python installed on your computer with a minimum version of 3.6 or higher.</li><li>Use command prompt (Windows) or terminal (Mac) to install FastAPI with the command:<code>pip install fastapi</code>.</li><li>You may also need to install an ASGI server like Uvicorn to run your FastAPI project.</li><li>Create a new Python file for your FastAPI project, e.g.,<code>my_api.py</code>.</li><li>Import FastAPI into your Python file using<code>import fastapi</code>.</li><li>Create an instance of FastAPI using<code>app = fastapi.FastAPI()</code>.</li><li>Define endpoints using different HTTP methods like<code>GET</code>,<code>POST</code>,<code>PUT</code>,<code>DELETE</code>, etc.</li><li>Endpoints represent different operations or resources in your API.</li><li>You can use parameters in your endpoints, such as path parameters and query parameters, to customize API behavior.</li></ul><p>Once your FastAPI project is set up, you can run it using an ASGI server like Uvicorn. Test your API endpoints and explore the autogenerated documentation provided by FastAPI.</p><p>With FastAPI, you can quickly build powerful and efficient APIs with Python, making it an excellent choice for web development projects.</p>
"""

prompt7="""
As an Insight Summarizer, your task is to distill provided information into a concise and informative 
summary of around 250 words. Utilize bullet points or numbered lists to highlight key
 points and ensure clarity and coherence in your summary. Avoid injecting personal
opinions and focus solely on presenting the main insights from the content.
Ensure to structure the content using HTML tags like <p> for paragraphs and<ul>, <li> for list items. heading <b> tag , next line <br>  , dont use "\n" , instead use <br> instead for next line
 Here's an structure of output:
<p><b>Main Topic:[Main topic of the content]<b>
<br><ul>
<li>[Key point 1]: [Description or detail]</li>
<li>[Key point 2]: [Description or detail]</li>
<li>[Key point 3]: [Description or detail]</li>
</ul><br><b>Additional Considerations:<b><br><ul>
<li>[Additional consideration 1]: [Description or detail]</li>
<li>[Additional consideration 2]: [Description or detail]</li>
<li>[Additional consideration 3]: [Description or detail]</li>
</ul></p>
Your summary should provide a comprehensive overview of the content, enabling readers to understand the main insights efficiently. Remember to maintain objectivity and focus on the key points to ensure clarity and usefulness for the reader."

Example:
<p>Main Topic: <b>The Impact of Artificial Intelligence on Business</b>
<br>
<ul>
<li>AI enhances operational efficiency by automating repetitive tasks.</li>
<li>It improves decision-making through data analysis and predictive analytics.</li>
<li>AI-powered chatbots provide personalized customer support, enhancing customer satisfaction.</li>
</ul><br><b>Additional Considerations:</b>
<br><ul>
<li>AI may raise ethical concerns regarding data privacy and job displacement.</li>
<li>Investing in AI requires significant financial resources for research and development.</li>
<li>Regulatory frameworks are necessary to govern AI implementation and mitigate risks.</li>
</ul></p>
"""


prompt3="""
As a web assistant, your task is to generate relevant answers in 150 words
based on the provided user's question by using the provided web content. The answers should accurately reflect the information provided
 in the summary without introducing any personal opinions or irrelevant details.if suggestions are asked 
 provide the accurate suggestion on your own based on the topic , if the response is lenghty you can represent 
 it in the pointwise  
 """

prompt4="""
As a web assistant, your task is to generate concise and relevant 
answers in 150 words based on the provided user's question and the
accompanying web content. The answers should accurately reflect the
information provided in the summary without introducing any personal 
opinions or irrelevant details. If suggestions are requested, provide 
accurate recommendations based on the topic. If the response is lengthy,
represent it in a pointwise format and dont mention 
the user question again in the output.

Here is the content from the parsed web page: {transcript}. 

User's Question: {question}

and dont provide the additional information other than the asked question 

Ensure to structure the content using HTML tags like <p> for paragraphs and<ul>, <li> for list items. heading <b> tag , next line <br>  , dont use "\n" , instead use <br> instead for next line , give output  with <p> end with </p> tag

Example:
<p><b>Main Topic:The Impact of Artificial Intelligence on Business</b><br><ul><li>AI enhances operational efficiency by automating repetitive tasks.</li><li>It improves decision-making through data analysis and predictive analytics.</li><li>AI-powered chatbots provide personalized customer support, enhancing customer satisfaction.</li></ul><br></p>

"""

prompt5="""you are a youtube video sumaeizer, you will be taking the transcript text
and summmarize the entire video and providing the importand summary in points
with 200 words .please provide the summary and make it pointwise in depth  .
Ensure to structure the content using HTML tags like <p> for paragraphs and<ul>, <li> for list items. heading <b> tag , next line <br>  , dont use "\n" , instead use <br> instead for next line
 
Your summary should provide a comprehensive overview of the full content, enabling readers to understand the main insights efficiently. Remember to maintain objectivity and focus on the key points to ensure clarity and usefulness for the reader. i give just a example with short content but add more content in para tag, generate content based on the type of content give"

Example  if the content is about tutorial or instruction:
<p><b>Main Topic: Creating a Website from Scratch with HTML and CSS</b><p><strong>Step 1: Planning Your Website</strong></p><p>Before diving into coding, take some time to plan your website's structure, layout, and content. Consider the purpose of your website, target audience, and desired features. Sketch out wireframes or create mockups to visualize the design and user experience.</p><p><strong>Step 2: Setting Up Your Development Environment</strong></p><p>Ensure you have a text editor installed, such as Visual Studio Code or Sublime Text, for writing HTML and CSS code. Create a new project folder and organize your files neatly. Optionally, consider using version control systems like Git to track changes and collaborate with others.</p><p><strong>Step 3: Creating the HTML Structure</strong></p><p>Start by creating the basic structure of your website using HTML</p><p><strong>Step 4: Adding Content and Text</strong></p><p>Populate your website with relevant content, including headings, paragraphs, images, and links. Use descriptive text to communicate your message effectively and engage users. Organize content logically to improve readability and navigation.</p><p><strong>Step 5: Styling with CSS</strong></p><p>Apply styles to your website using CSS to enhance its appearance and layout. Create a separate CSS file and link it to your HTML document using the<link>tag. Use selectors, properties, and values to customize fonts, colors, margins, padding, and more.</p><p><strong>Step 6: Implementing Responsive Design</strong></p><p>Ensure your website looks great and functions well across various devices and screen sizes. Use media queries and flexible layout techniques to create a responsive design that adapts to desktops, laptops, tablets, and smartphones seamlessly.</p><p><strong>Step 7: Adding Navigation Menus</strong></p><p>Implement navigation menus to help users navigate your website easily. Create a header or sidebar menu using HTML lists , and style it with CSS to enhance its appearance. Consider adding hover effects and transitions for better user interaction.</p><p><strong>Step 8: Incorporating Multimedia Elements</strong></p><p>Enhance your website with multimedia elements such as images, videos, and audio files. Use the image video tags to embed media content directly into your web pages. Optimize multimedia files for faster loading times and better performance.</p><p><strong>Step 9: Implementing Forms and Interactivity</strong></p><p>Add interactive elements to your website, such as forms, buttons, and animations, to engage users and collect feedback. Use HTML form elements like <input>,<textarea>, and <button> to create user-friendly forms for inputting data.</p><p><strong>Step 10: Testing and Debugging</strong></p><p>Thoroughly test your website across different browsers and devices to ensure compatibility and functionality. Use developer tools to inspect and debug your code, fix any errors or inconsistencies, and optimize performance. Solicit feedback from peers or beta testers to identify areas for improvement.</p><p><strong>Step 11: Deploying Your Website</strong></p><p>Once you're satisfied with your website's design and functionality, it's time to deploy it to a web server. Choose a reliable hosting provider and upload your files using FTP or file manager tools. Configure domain settings and ensure proper security measures are in place.</p></p>

 """

content=""
transcript=""

def scrweb(url):
    global content
    if not validators.url(url):
        status=400
        response="enter correct url"
        return status,response
    else:
        web=requests.get(url)
        status=web.status_code
        if status==200:
            soup=BeautifulSoup(web.content,"html.parser")
            paragraphs = soup.find_all(["p", "h1", "h2"])
            text_list = [p.get_text() for p in paragraphs]

            # Combine text from all paragraphs into a single string
            content = ''.join(text_list)

            return status,content
        else:
            return {"unable to retrieve "}


def genetate_gemini_content(prompt,content):
    response=model.generate_content([prompt,content])
    return response.text

def extract_transcript(youtube_link):
    try:
        global transcript
        if not validators.url(youtube_link):
            status=400
            response="enter correct url"
            return status,response
        else:
            video_id=youtube_link.split("=")[1].split("&")[0]
            transcript_text=YouTubeTranscriptApi.get_transcript(video_id,languages = [ 'en'])

            for i in transcript_text:
                transcript+=" "+i["text"]
            return transcript
         
    except Exception as e:
            return "no information avaliable"
 
   
@app.get("/summary")
async def test(url:str):
    try:
        status,content=scrweb(url)
        if status==200:
            response=genetate_gemini_content(prompt6,content)
            return response
        else:
            return status

    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/ut")
async def test():
    global transcript
    return transcript

@app.get("/wb")
async def test():
    global content
    return content


@app.post("/webqa")
async def webchat(question:str):
    global content
    try:
        if content:
            response=model.generate_content([prompt4,content,question])
            return response.text 
        else:
            return {"please summarize first"}
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        



@app.get("/youtube")
async def ytranscript(url : str):
    try:
        transcript_text=extract_transcript(url)
        if transcript_text:
            print(transcript_text)
            response=model.generate_content([prompt6,transcript_text])
            return response.text
        
        else:
            return {"unable to retrieve data"}
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")

    
@app.post("/ytqanda")
async def ytchat(question:str):
    global transcript
    try:
        if transcript:
            response=model.generate_content([prompt4,transcript,question])
            return response.text 
        else:
            return {"please summarize first"}
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        
@app.get("/")
async def test():
    return {"api is running"}
    
@app.get("/rm")
async def rm():
    global transcript
    global content
    transcript=""
    content=""
    return
