from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException 
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
import requests
from bs4 import BeautifulSoup
import validators
from youtube_transcript_api import YouTubeTranscriptApi


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
example is given below , just dont display example itself just follow the structure
Example:
<p><b>Main Topic: Gardening Basics - A Beginner's Guide</b></p><p>Gardening is a fulfilling hobby that connects you with nature and allows you to create beautiful outdoor spaces. In this guide, Emma will walk you through the basics of gardening, helping you get started on your gardening journey.</p><p>Gardening involves cultivating and nurturing plants, flowers, and vegetables in outdoor spaces such as gardens, balconies, or even windowsills.</p><p>Here are some key points to remember:</p><ul><li>Choose a suitable location for your garden, considering factors like sunlight, soil quality, and drainage.</li><li>Prepare the soil by loosening it and adding compost or organic matter to improve its texture and fertility.</li><li>Select plants that are well-suited to your local climate and growing conditions. Consider factors like temperature, humidity, and rainfall.</li><li>Plant your garden using proper spacing and planting techniques. Follow instructions on seed packets or plant tags for best results.</li><li>Water your garden regularly, ensuring plants receive adequate moisture without being overwatered.</li><li>Monitor for pests and diseases, taking proactive measures to protect your plants and maintain their health.</li><li>Prune and trim plants as needed to promote growth and maintain their shape.</li><li>Harvest fruits, vegetables, and flowers when they are ripe, enjoying the bounty of your garden.</li><li>Take time to relax and enjoy your garden, whether it's sitting amongst the flowers, watching birds and butterflies, or simply soaking in the beauty of nature.</li></ul><p>As you gain experience and confidence in gardening, you can explore more advanced techniques and experiment with different plants and garden designs.</p><p>Gardening is not only a rewarding hobby but also a way to connect with the earth and cultivate a sense of wellbeing and stewardship for the environment.</p>
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
            print(response)
            return response
        else:
            return status

    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")


    

@app.get("/ut")
async def test():
    global transcript
    # Check if the input is a valid URL
    # if not validators.url(url):
    #     raise HTTPException(status_code=400, detail="Invalid URL")
    
    return transcript

@app.get("/wb")
async def test():
    global content
    # Check if the input is a valid URL
    # if not validators.url(url):
    #     raise HTTPException(status_code=400, detail="Invalid URL")
    
    return content



@app.post("/webqa")
async def webchat(question:str):
    global content
    try:
        if content:
            response=model.generate_content([prompt4,content,question])
            print(response.text)
            return response.text 
        else:
            return {"please summarize first"}
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        


@app.get("/youtube")
async def ytranscript(url : str):
    global transcript
    transcript_text=extract_transcript(url)
    print(transcript_text)
    if transcript_text:
        try:
            print("hi")
            response=model.generate_content([prompt6,transcript_text])
            print(response.text)
            return response.text
        except:
            raise HTTPException(status_code=500, detail="Internal Server Error")

    
@app.post("/ytqanda")
async def ytchat(question:str):
    global transcript
    try:
        if transcript:
            response=model.generate_content([prompt4,transcript,question])
            print(response.text)
            return response.text 
        else:
            return {"please summarize first"}
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        
@app.get("/")
async def test():
    return {"status":"api is working"}


@app.get("/rm")
async def rm():
    global transcript
    global content
    transcript=""
    content=""
    print("removed")
    return
