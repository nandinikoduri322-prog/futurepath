import streamlit as st
import random
import hashlib
import re
import sqlite3
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta

st.set_page_config(page_title="FuturePath", page_icon="favicon.png", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp{background:linear-gradient(135deg,#f8f3ff,#eef7ff 45%,#fff1f7)}
.hero{padding:32px;border-radius:28px;background:linear-gradient(135deg,#7c3aed,#2563eb,#ec4899);color:white;text-align:center;margin-bottom:24px}
.hero h1{font-size:56px;margin:0;font-weight:900}.hero h2{font-size:25px}.hero p{font-size:17px}
.card{background:white;padding:18px;border-radius:18px;border:1px solid #e5e7eb;box-shadow:0 6px 18px rgba(0,0,0,.07);margin-bottom:12px}
.footer{text-align:center;padding:25px;color:#667085}
</style>
""", unsafe_allow_html=True)

# ============================================================
# COMPLETE ENGINEERING DATA
# Each branch has B.Tech -> M.Tech -> MS pathways.
# Course names are common examples; availability varies by university.
# ============================================================

def E(category, icon, description, subjects, skills, projects, internships, careers, mtech, ms):
    return dict(category=category, icon=icon, description=description, subjects=subjects,
                skills=skills, projects=projects, internships=internships, careers=careers,
                mtech=mtech, ms=ms)

BRANCHES = {
"CSE": E("Computer & Technology","💻","Computer Science Engineering covers programming, algorithms, software, databases and computer systems.",
["Programming","Data Structures & Algorithms","DBMS","Operating Systems","Computer Networks","Software Engineering","Web Technologies"],
["Python/Java/C++","SQL","Git/GitHub","Web Development","Problem Solving","Cloud Basics"],
["College ERP","Student Management System","Online Quiz Platform","Placement Portal"],
["Software Developer Intern","Web Developer Intern","Backend Intern","QA Intern"],
["Software Developer","Full Stack Developer","Backend Engineer","Cloud Engineer","System Engineer"],
["M.Tech Computer Science & Engineering","M.Tech Software Engineering","M.Tech Computer Networks","M.Tech Information Security","M.Tech Cloud Computing","M.Tech AI & Machine Learning"],
["MS Computer Science","MS Software Engineering","MS Information Systems","MS Cybersecurity","MS Artificial Intelligence","MS Computer Engineering","MS Data Science"]),

"CSD": E("Computer & Data","📊","Computer Science and Data Science combines computing, statistics, data analysis and machine learning.",
["Python Programming","Statistics","DBMS","Data Structures","Data Mining","Machine Learning","Data Visualization"],
["Python","SQL","Pandas","NumPy","Statistics","Power BI/Tableau","Machine Learning"],
["Student Performance Predictor","Placement Analytics","Attendance Dashboard","College Data Warehouse"],
["Data Analyst Intern","Data Science Intern","BI Intern","ML Intern"],
["Data Scientist","Data Analyst","BI Analyst","ML Engineer","Analytics Engineer"],
["M.Tech Data Science","M.Tech Artificial Intelligence","M.Tech Machine Learning","M.Tech Computer Science","M.Tech Big Data Analytics","M.Tech Business Analytics"],
["MS Data Science","MS Analytics","MS Business Analytics","MS Computer Science","MS Artificial Intelligence","MS Machine Learning"]),

"CSM": E("Computer & AI","🤖","Computer Science and Machine Learning combines software engineering with machine learning and intelligent systems.",
["Programming","Data Structures","Statistics","Machine Learning","Deep Learning","NLP","Computer Vision"],
["Python","Scikit-learn","TensorFlow/PyTorch","SQL","Git","Model Evaluation"],
["Spam Detection","Score Prediction","Image Classifier","Recommendation System"],
["ML Intern","AI Intern","Data Science Intern","Software Intern"],
["ML Engineer","AI Engineer","Data Scientist","Computer Vision Engineer","NLP Engineer"],
["M.Tech AI & Machine Learning","M.Tech Machine Learning","M.Tech Artificial Intelligence","M.Tech Computer Science","M.Tech Data Science","M.Tech Robotics & AI"],
["MS Artificial Intelligence","MS Machine Learning","MS Computer Science","MS Data Science","MS Robotics","MS Computer Vision"]),

"Artificial Intelligence & ML": E("Computer & AI","🧠","AI and ML focuses on systems that learn from data and perform intelligent tasks.",
["Python","Statistics","Machine Learning","Deep Learning","NLP","Computer Vision","Generative AI"],
["Python","ML Libraries","Deep Learning","LLMs","Prompt Design","Model Evaluation"],
["AI Chatbot","Image Classifier","Recommendation Engine","RAG Question Answering"],
["AI Intern","ML Intern","NLP Intern","Computer Vision Intern"],
["AI Engineer","ML Engineer","NLP Engineer","Computer Vision Engineer","Generative AI Engineer"],
["M.Tech AI","M.Tech AI & ML","M.Tech Machine Learning","M.Tech Data Science","M.Tech Computer Science","M.Tech Robotics & AI"],
["MS Artificial Intelligence","MS Machine Learning","MS Computer Science","MS Data Science","MS Robotics","MS Human-Centered AI"]),

"Data Science": E("Computer & Data","📈","Data Science uses programming, statistics and machine learning to turn data into useful insights.",
["Python","Statistics","Probability","SQL/DBMS","Data Mining","Machine Learning","Data Visualization"],
["Python","SQL","Pandas/NumPy","Power BI","Statistics","Machine Learning","Communication"],
["Student Performance Predictor","Hospital Data Analysis","Placement Predictor","Sales Forecasting"],
["Data Analyst Intern","Data Science Intern","BI Intern","ML Intern"],
["Data Scientist","Data Analyst","ML Engineer","BI Analyst","Analytics Engineer"],
["M.Tech Data Science","M.Tech AI & ML","M.Tech Machine Learning","M.Tech Big Data Analytics","M.Tech Computer Science","M.Tech Business Analytics"],
["MS Data Science","MS Analytics","MS Business Analytics","MS Computer Science","MS Artificial Intelligence","MS Statistics"]),

"Cyber Security": E("Computer & Security","🔐","Cyber Security protects systems, networks, applications and information from attacks and misuse.",
["Computer Networks","Operating Systems","Cryptography","Network Security","Ethical Hacking","Digital Forensics","Secure Coding"],
["Linux","Networking","Python","Security Tools","Web Security","Incident Analysis"],
["Secure Login System","Password Audit Tool","Network Monitoring Dashboard","Web Security Lab"],
["Cyber Security Intern","SOC Intern","Security Analyst Intern","Penetration Testing Intern"],
["Security Analyst","SOC Analyst","Cyber Security Engineer","Penetration Tester","Digital Forensics Analyst"],
["M.Tech Cyber Security","M.Tech Information Security","M.Tech Network Security","M.Tech Computer Science","M.Tech Digital Forensics","M.Tech Cyber Forensics"],
["MS Cybersecurity","MS Information Security","MS Computer Science","MS Digital Forensics","MS Network Security","MS Cyber Defense"]),

"Information Technology": E("Computer & Technology","🖥️","Information Technology focuses on software, databases, networks, cloud services and IT operations.",
["Programming","DBMS","Computer Networks","Operating Systems","Web Technology","Cloud Computing","IT Service Management"],
["Python/Java","SQL","Linux","Cloud","Networking","Web Development","Git"],
["College ERP","Inventory System","IT Help Desk","Cloud File Manager"],
["IT Support Intern","Cloud Intern","Software Intern","System Admin Intern"],
["IT Engineer","System Administrator","Cloud Engineer","Software Developer","Network Engineer"],
["M.Tech IT","M.Tech Computer Science","M.Tech Cloud Computing","M.Tech Network Management","M.Tech Information Security","M.Tech Software Engineering"],
["MS Information Technology","MS Information Systems","MS Computer Science","MS Cybersecurity","MS Cloud Computing"]),

"Prompt Engineering & Generative AI": E("AI / Emerging","✨","Prompt Engineering is an emerging AI skill pathway focused on designing, testing and evaluating prompts and AI workflows. It is not a universally offered standalone B.Tech branch; it can be pursued through AI/CSE/Data Science specializations, electives and projects.",
["Generative AI","LLM Basics","Prompt Design","NLP Basics","RAG","AI Evaluation","AI Ethics"],
["Prompt Design","Python","API Usage","Evaluation","RAG","AI Safety","Technical Writing"],
["College AI Assistant","Study Assistant with RAG","Prompt Evaluation Benchmark","Resume Feedback Assistant"],
["Generative AI Intern","AI Product Intern","LLM/RAG Intern","AI Automation Intern"],
["Generative AI Engineer","AI Application Developer","AI Automation Specialist","AI Product Associate","LLM Application Engineer"],
["M.Tech AI","M.Tech AI & ML","M.Tech Data Science","M.Tech Computer Science","M.Tech NLP","M.Tech Intelligent Systems"],
["MS Artificial Intelligence","MS Computer Science","MS Data Science","MS NLP","MS Human-Centered AI"]),

"Internet of Things": E("Emerging Technology","🌐","IoT connects sensors, devices, embedded systems, networks and cloud platforms.",
["Sensors","Microcontrollers","Embedded Systems","IoT Networking","Cloud IoT","Data Analytics","Control Systems"],
["C/C++","Python","Arduino/ESP32","Sensors","MQTT","Cloud","Networking"],
["Smart Irrigation","Smart Home","Air Quality Monitor","Smart Parking"],
["IoT Intern","Embedded Intern","Automation Intern","IoT Cloud Intern"],
["IoT Engineer","Embedded Engineer","Automation Engineer","IoT Cloud Engineer"],
["M.Tech IoT","M.Tech Embedded Systems","M.Tech VLSI","M.Tech Communication Systems","M.Tech AI & IoT","M.Tech Automation"],
["MS IoT","MS Embedded Systems","MS Computer Engineering","MS Electrical Engineering","MS Robotics"]),

"ECE": E("Electronics & Electrical","📡","Electronics and Communication Engineering covers electronics, communication, embedded systems and signal processing.",
["Analog Electronics","Digital Electronics","Signals & Systems","Communication Systems","Microprocessors","Embedded Systems","VLSI"],
["Embedded C","Microcontrollers","Digital Electronics","PCB Basics","MATLAB","Communication"],
["Smart Traffic Light","Home Automation","Temperature Monitor","IoT Device"],
["Embedded Intern","Electronics Intern","VLSI Intern","Communication Intern"],
["Embedded Engineer","Electronics Engineer","VLSI Engineer","Communication Engineer","Hardware Engineer"],
["M.Tech ECE","M.Tech VLSI Design","M.Tech Embedded Systems","M.Tech Communication Systems","M.Tech Signal Processing","M.Tech Microelectronics"],
["MS Electrical & Computer Engineering","MS Electronics","MS Embedded Systems","MS VLSI","MS Telecommunications"]),

"EEE": E("Electrical & Power","⚡","Electrical and Electronics Engineering covers electrical machines, power systems, control and power electronics.",
["Circuit Theory","Electrical Machines","Power Systems","Power Electronics","Control Systems","Electrical Measurements","Renewable Energy"],
["MATLAB","Circuit Analysis","Power Systems","PLC Basics","Control Systems","Electrical Design"],
["Solar Power Monitor","Smart Energy Meter","Automatic Street Light","Motor Control System"],
["Electrical Intern","Power Systems Intern","Maintenance Intern","Renewable Energy Intern"],
["Electrical Engineer","Power Engineer","Control Engineer","Renewable Energy Engineer"],
["M.Tech Power Systems","M.Tech Power Electronics","M.Tech Control Systems","M.Tech Electrical Engineering","M.Tech Renewable Energy","M.Tech High Voltage Engineering"],
["MS Electrical Engineering","MS Power Systems","MS Power Electronics","MS Control Systems","MS Energy Systems"]),

"Mechanical": E("Core Engineering","⚙️","Mechanical Engineering deals with machines, design, manufacturing, thermal systems and automation.",
["Engineering Mechanics","Thermodynamics","Fluid Mechanics","Machine Design","Manufacturing","Heat Transfer","CAD/CAM"],
["AutoCAD/SolidWorks","CAD","Manufacturing","3D Printing","Thermodynamics","Automation"],
["Mini Solar Vehicle","Automatic Conveyor","3D CAD Model","Robotic Arm"],
["Mechanical Intern","Design Intern","Production Intern","Manufacturing Intern"],
["Mechanical Engineer","Design Engineer","Production Engineer","Manufacturing Engineer","CAD Engineer"],
["M.Tech Mechanical Engineering","M.Tech Machine Design","M.Tech Thermal Engineering","M.Tech Manufacturing","M.Tech CAD/CAM","M.Tech Industrial Engineering"],
["MS Mechanical Engineering","MS Manufacturing","MS Robotics","MS Mechatronics","MS Automotive Engineering","MS Energy Systems"]),

"Civil": E("Core Engineering","🏗️","Civil Engineering focuses on buildings, roads, bridges, construction, water resources and infrastructure.",
["Engineering Mechanics","Surveying","Structural Engineering","Geotechnical Engineering","Transportation","Hydraulics","Construction Management"],
["AutoCAD","Surveying","Structural Analysis","Quantity Estimation","Project Management","GIS Basics"],
["Smart Building Model","Rainwater Harvesting Plan","Road Design","Water Management Plan"],
["Site Engineer Intern","Civil Design Intern","Construction Intern","Surveying Intern"],
["Civil Engineer","Structural Engineer","Site Engineer","Transportation Engineer","Construction Manager"],
["M.Tech Structural Engineering","M.Tech Geotechnical Engineering","M.Tech Transportation Engineering","M.Tech Environmental Engineering","M.Tech Water Resources","M.Tech Construction Management","M.Tech Structural Engineering"],
["MS Civil Engineering","MS Structural Engineering","MS Construction Management","MS Transportation Engineering","MS Environmental Engineering","MS Water Resources"]),

"Chemical": E("Core Engineering","🧪","Chemical Engineering applies chemistry, mathematics and engineering to industrial processes and production.",
["Chemical Process Calculations","Thermodynamics","Fluid Mechanics","Heat Transfer","Mass Transfer","Reaction Engineering","Process Control"],
["Process Design","Process Simulation","Safety","Quality Control","Data Analysis","Plant Operations"],
["Water Treatment Model","Process Simulation","Waste Reduction Study","Heat Exchanger Analysis"],
["Process Intern","Quality Intern","Production Intern","Chemical Plant Intern"],
["Chemical Engineer","Process Engineer","Production Engineer","Quality Engineer","Safety Engineer"],
["M.Tech Chemical Engineering","M.Tech Process Engineering","M.Tech Petroleum Engineering","M.Tech Environmental Engineering","M.Tech Energy Engineering","M.Tech Industrial Engineering"],
["MS Chemical Engineering","MS Process Engineering","MS Energy Engineering","MS Environmental Engineering","MS Materials Science"]),

"Agricultural Engineering": E("Agriculture & Life Sciences","🌾","Agricultural Engineering applies engineering, sensors and technology to farming, irrigation, machinery and post-harvest systems.",
["Farm Machinery","Irrigation Engineering","Soil & Water Engineering","Agricultural Processing","Renewable Energy","Sensors & Automation"],
["CAD","Sensors","Irrigation","Data Analysis","Farm Machinery","GIS Basics"],
["Smart Irrigation","Crop Monitoring","Soil Moisture System","Solar Farm Model"],
["Agri-Tech Intern","Farm Technology Intern","Irrigation Intern","Food Processing Intern"],
["Agricultural Engineer","Agri-Tech Specialist","Irrigation Engineer","Farm Machinery Engineer"],
["M.Tech Agricultural Engineering","M.Tech Soil & Water Engineering","M.Tech Farm Machinery","M.Tech Food Processing","M.Tech Renewable Energy","M.Tech Remote Sensing/GIS"],
["MS Agricultural Engineering","MS Biosystems Engineering","MS Food Science","MS Environmental Engineering","MS Precision Agriculture"]),

"Biotechnology": E("Life Sciences","🧬","Biotechnology combines biology, chemistry and technology for healthcare, agriculture, food and research.",
["Cell Biology","Genetics","Biochemistry","Microbiology","Molecular Biology","Bioprocess Engineering","Bioinformatics"],
["Laboratory Skills","Bioinformatics","Data Analysis","Molecular Techniques","Scientific Communication"],
["Plant Growth Study","Bioinformatics Analysis","Food Microbiology Study","DNA Sequence Analysis"],
["Biotech Intern","Lab Intern","Research Intern","Bioinformatics Intern"],
["Biotechnologist","Research Associate","Bioinformatics Associate","Lab Analyst"],
["M.Tech Biotechnology","M.Tech Bioinformatics","M.Tech Bioprocess Engineering","M.Tech Genetic Engineering","M.Tech Biomedical Engineering"],
["MS Biotechnology","MS Bioinformatics","MS Molecular Biology","MS Biomedical Engineering","MS Computational Biology"]),

"Food Technology": E("Food & Life Sciences","🍎","Food Technology covers food processing, preservation, quality, safety, packaging and product development.",
["Food Chemistry","Food Microbiology","Food Processing","Food Safety","Quality Control","Packaging","Food Engineering"],
["Food Testing","Quality Control","Processing","Packaging","Food Safety","Data Analysis"],
["Food Quality Study","Shelf-Life Analysis","Food Packaging Design","Food Safety Dashboard"],
["Food Quality Intern","Production Intern","R&D Intern","Food Safety Intern"],
["Food Technologist","Quality Analyst","Production Executive","Food Safety Officer"],
["M.Tech Food Technology","M.Tech Food Processing","M.Tech Food Engineering","M.Tech Food Safety","M.Tech Biotechnology"],
["MS Food Science","MS Food Technology","MS Food Safety","MS Food Engineering","MS Biotechnology"]),

"Textile Technology": E("Core Engineering","🧵","Textile Technology covers fibers, yarns, fabrics, processing, garment production and textile quality.",
["Textile Fibers","Yarn Technology","Fabric Technology","Textile Chemistry","Garment Technology","Textile Testing"],
["Textile Materials","CAD","Quality Control","Production","Textile Testing","Design"],
["Fabric Quality Analysis","Smart Textile Concept","Textile Waste Study","Fabric Testing Dashboard"],
["Textile Intern","Production Intern","Quality Intern","Garment Intern"],
["Textile Engineer","Quality Engineer","Production Engineer","Textile Technologist"],
["M.Tech Textile Engineering","M.Tech Textile Technology","M.Tech Textile Chemistry","M.Tech Fashion Technology","M.Tech Industrial Engineering"],
["MS Textile Engineering","MS Materials Science","MS Fashion Technology","MS Manufacturing"]),

"Aerospace / Aeronautical": E("Aerospace & Aviation","✈️","Aerospace Engineering focuses on aircraft, spacecraft, aerodynamics, propulsion and flight systems.",
["Aerodynamics","Aircraft Structures","Propulsion","Flight Mechanics","Avionics Basics","Aerospace Materials","Control Systems"],
["CAD","Aerodynamics","Simulation","Programming","Flight Data Analysis","Materials"],
["Drone Concept","Aircraft Model","Flight Data Analysis","UAV Monitoring System"],
["Aerospace Intern","Design Intern","Flight Systems Intern","UAV Intern"],
["Aerospace Engineer","Aeronautical Engineer","Design Engineer","Flight Systems Engineer"],
["M.Tech Aerospace Engineering","M.Tech Aeronautical Engineering","M.Tech Propulsion","M.Tech Flight Mechanics","M.Tech Avionics","M.Tech Aerospace Structures"],
["MS Aerospace Engineering","MS Aeronautics","MS Astronautics","MS Aviation","MS Mechanical Engineering"]),

"Automobile": E("Core Engineering","🚗","Automobile Engineering focuses on vehicle design, manufacturing, vehicle systems and electric mobility.",
["Vehicle Dynamics","Automotive Engines","Automotive Electronics","Vehicle Design","Manufacturing","EV Technology"],
["CAD","Vehicle Systems","Automotive Electronics","EV Basics","Diagnostics","Manufacturing"],
["Mini Electric Vehicle","Vehicle Monitoring System","EV Battery Monitor","Vehicle Safety System"],
["Automobile Intern","EV Intern","Design Intern","Automotive Service Intern"],
["Automobile Engineer","EV Engineer","Vehicle Design Engineer","Automotive Test Engineer"],
["M.Tech Automobile Engineering","M.Tech Automotive Engineering","M.Tech Electric Vehicle Technology","M.Tech Mechanical Engineering","M.Tech Manufacturing"],
["MS Automotive Engineering","MS Mechanical Engineering","MS Electric Vehicle Engineering","MS Mobility Systems"]),

"Robotics & Automation": E("Emerging Technology","🤖","Robotics and Automation combines mechanical systems, electronics, sensors, control and programming.",
["Robotics","Control Systems","Sensors","Embedded Systems","Robot Kinematics","Automation","Computer Vision"],
["Python/C++","ROS Basics","Sensors","Arduino/ESP32","CAD","Control Systems"],
["Line Following Robot","Obstacle Avoiding Robot","Automatic Sorting System","Robotic Arm"],
["Robotics Intern","Automation Intern","Embedded Intern","Computer Vision Intern"],
["Robotics Engineer","Automation Engineer","Control Engineer","Robotics Software Engineer"],
["M.Tech Robotics","M.Tech Automation","M.Tech Mechatronics","M.Tech Control Systems","M.Tech AI & Robotics"],
["MS Robotics","MS Mechatronics","MS Automation","MS Computer Vision","MS Mechanical Engineering"]),

"Industrial Engineering": E("Core Engineering","🏭","Industrial Engineering improves productivity, quality, processes, operations and resource utilization.",
["Operations Research","Production Planning","Quality Engineering","Statistics","Supply Chain","Ergonomics","Industrial Automation"],
["Excel","Statistics","Data Analysis","Lean Basics","Quality Tools","Process Improvement"],
["Production Dashboard","Process Optimization","Inventory Analysis","Quality Improvement Study"],
["Operations Intern","Quality Intern","Process Improvement Intern","Supply Chain Intern"],
["Industrial Engineer","Operations Analyst","Quality Engineer","Supply Chain Analyst"],
["M.Tech Industrial Engineering","M.Tech Production Engineering","M.Tech Manufacturing","M.Tech Operations Research","M.Tech Supply Chain"],
["MS Industrial Engineering","MS Manufacturing","MS Operations Research","MS Supply Chain Management","MS Engineering Management"]),

"Mining Engineering": E("Core Engineering","⛏️","Mining Engineering covers safe and efficient extraction, mine planning, surveying and mineral processing.",
["Mining Methods","Mine Surveying","Rock Mechanics","Mine Ventilation","Mineral Processing","Mine Safety"],
["Surveying","Mine Planning","Safety","CAD","Data Analysis","GIS"],
["Mine Safety Dashboard","Mining Survey Model","Resource Analysis","Ventilation Study"],
["Mining Intern","Safety Intern","Survey Intern","Mine Planning Intern"],
["Mining Engineer","Mine Planning Engineer","Safety Engineer","Survey Engineer"],
["M.Tech Mining Engineering","M.Tech Mine Planning","M.Tech Rock Mechanics","M.Tech Mineral Processing","M.Tech Mine Safety"],
["MS Mining Engineering","MS Mineral Processing","MS Geological Engineering","MS Environmental Engineering"]),

"Marine Engineering": E("Core Engineering","🚢","Marine Engineering focuses on ship machinery, propulsion, marine systems and maintenance.",
["Marine Engines","Thermodynamics","Marine Electrical Systems","Ship Construction","Fluid Mechanics","Marine Safety"],
["Mechanical Skills","Maintenance","Thermodynamics","Marine Systems","Safety"],
["Ship Propulsion Model","Marine Monitoring System","Engine Efficiency Study"],
["Marine Intern","Engine Intern","Maintenance Intern","Shipyard Intern"],
["Marine Engineer","Marine Systems Engineer","Maintenance Engineer","Ship Machinery Engineer"],
["M.Tech Marine Engineering","M.Tech Ocean Engineering","M.Tech Naval Architecture","M.Tech Mechanical Engineering"],
["MS Marine Engineering","MS Ocean Engineering","MS Naval Architecture","MS Mechanical Engineering"]),

"Biomedical Engineering": E("Life Sciences","🩺","Biomedical Engineering combines engineering, biology and healthcare technology.",
["Biomedical Instrumentation","Biomaterials","Medical Imaging","Biomechanics","Signals & Systems","Medical Devices"],
["Sensors","Electronics","Programming","Medical Instrumentation","Data Analysis"],
["Heart Rate Monitor","Patient Monitoring Demo","Health Tracking App","Medical Sensor Prototype"],
["Biomedical Intern","Medical Device Intern","Clinical Engineering Intern","Research Intern"],
["Biomedical Engineer","Medical Device Engineer","Clinical Engineer","Biomedical Research Associate"],
["M.Tech Biomedical Engineering","M.Tech Medical Instrumentation","M.Tech Biomedical Signal Processing","M.Tech Biomaterials","M.Tech Biotechnology"],
["MS Biomedical Engineering","MS Medical Devices","MS Bioengineering","MS Biomaterials","MS Biomedical Imaging"]),

"Environmental Engineering": E("Environment & Sustainability","🌱","Environmental Engineering focuses on pollution control, water, wastewater, waste management and sustainability.",
["Water Treatment","Wastewater Engineering","Air Pollution Control","Solid Waste Management","Environmental Chemistry","Environmental Monitoring"],
["Water Testing","Data Analysis","GIS Basics","Waste Management","Environmental Monitoring"],
["Air Quality Dashboard","Waste Segregation Study","Water Quality Analysis","Rainwater Harvesting Model"],
["Environmental Intern","Sustainability Intern","Water Quality Intern","Waste Management Intern"],
["Environmental Engineer","Water Engineer","Sustainability Analyst","Environmental Consultant"],
["M.Tech Environmental Engineering","M.Tech Water Resources","M.Tech Environmental Management","M.Tech Renewable Energy","M.Tech Public Health Engineering"],
["MS Environmental Engineering","MS Sustainability","MS Water Resources","MS Environmental Science","MS Energy & Environment"]),

"Energy Engineering": E("Energy & Sustainability","🔋","Energy Engineering focuses on renewable energy, energy systems, efficiency and sustainable technologies.",
["Energy Systems","Solar Energy","Wind Energy","Energy Storage","Power Systems","Energy Efficiency","Energy Economics"],
["Energy Analysis","Solar Basics","Data Analysis","Electrical Basics","Sustainability"],
["Solar Energy Monitor","Energy Consumption Dashboard","Smart Energy System","Battery Performance Analysis"],
["Energy Intern","Solar Intern","Renewable Energy Intern","Sustainability Intern"],
["Energy Engineer","Renewable Energy Engineer","Energy Analyst","Sustainability Engineer"],
["M.Tech Energy Engineering","M.Tech Renewable Energy","M.Tech Energy Systems","M.Tech Power Systems","M.Tech Sustainable Energy"],
["MS Energy Systems","MS Renewable Energy","MS Sustainable Energy","MS Environmental Engineering","MS Energy Economics"]),

"Avionics": E("Electronics & Aviation","🛩️","Avionics focuses on electronic, communication, navigation and control systems used in aircraft.",
["Aircraft Electronics","Navigation Systems","Communication Systems","Embedded Systems","Control Systems","Radar Basics"],
["Embedded C","Electronics","Control Systems","Programming","Communication"],
["Flight Data Display","Navigation Concept","Drone Control System","Telemetry Prototype"],
["Avionics Intern","Embedded Intern","Electronics Intern","Flight Systems Intern"],
["Avionics Engineer","Embedded Engineer","Flight Systems Engineer","Aircraft Electronics Engineer"],
["M.Tech Avionics","M.Tech Aerospace Engineering","M.Tech Embedded Systems","M.Tech Communication Systems","M.Tech Control Systems"],
["MS Avionics","MS Aerospace Engineering","MS Electrical Engineering","MS Embedded Systems","MS Control Systems"]),

"Materials Engineering": E("Core Engineering","🔬","Materials Engineering studies materials, properties, processing, testing and engineering applications.",
["Materials Science","Material Characterization","Metallurgy","Polymers","Ceramics","Composite Materials","Material Testing"],
["Material Testing","Chemistry","Manufacturing","Data Analysis","Quality Control"],
["Material Strength Study","Recycling Materials Study","Composite Material Model","Material Testing Dashboard"],
["Materials Intern","Quality Intern","R&D Intern","Materials Testing Intern"],
["Materials Engineer","Quality Engineer","R&D Engineer","Materials Scientist"],
["M.Tech Materials Engineering","M.Tech Metallurgy","M.Tech Nanotechnology","M.Tech Materials Science","M.Tech Polymer Technology"],
["MS Materials Science","MS Materials Engineering","MS Nanotechnology","MS Metallurgy","MS Chemical Engineering"]),
}

# ============================================================
# DIPLOMA / POLYTECHNIC — COMMON COURSES WITH CLEAR INFORMATION
# ============================================================
def D(description, subjects, skills, careers, further):
    return dict(description=description, subjects=subjects, skills=skills, careers=careers, further=further)

DIPLOMAS = {
"Diploma in Computer Engineering / CSE": D("A practical computer diploma covering programming, databases, hardware and software development.",["Programming","DBMS","Web Development","Computer Networks","Data Structures"],["Python/C/C++","SQL","Web Development","Troubleshooting"],["Junior Developer","IT Support Technician","Web Developer","Computer Technician"],["B.Tech lateral entry","BCA/related degree","Certifications","Apprenticeship"]),
"Diploma in Information Technology": D("Focuses on software, networking, databases, web technologies and IT support.",["Programming","DBMS","Networking","Web Technology","Operating Systems"],["SQL","Linux","Networking","Web Development"],["IT Technician","Support Associate","Junior Developer","Network Technician"],["B.Tech lateral entry","BCA","Certifications"]),
"Diploma in AI & Data Science": D("Introduces programming, statistics, data analysis and machine learning through practical work.",["Python","Statistics","SQL","Data Analytics","Machine Learning Basics"],["Python","Pandas","SQL","Excel/Power BI","Data Visualization"],["Data Analyst Trainee","Analytics Intern","Junior Data Technician"],["B.Tech lateral entry where available","Degree in Data/CS","Analytics certifications"]),
"Diploma in ECE": D("Covers electronics, communication, embedded systems and basic hardware design.",["Analog Electronics","Digital Electronics","Communication","Microcontrollers","Embedded Systems"],["Embedded C","Circuit Testing","Microcontrollers","PCB Basics"],["Electronics Technician","Embedded Trainee","Service Technician"],["B.Tech lateral entry ECE/related","Apprenticeship","Technical certifications"]),
"Diploma in EEE": D("Focuses on electrical circuits, machines, power systems and electrical maintenance.",["Electrical Circuits","Machines","Power Systems","Measurements","Control Basics"],["Electrical Testing","Wiring Basics","Machines","Safety"],["Electrical Technician","Maintenance Technician","Power Trainee"],["B.Tech lateral entry EEE/related","Apprenticeship","Electrical certifications"]),
"Diploma in Civil Engineering": D("Practical training in construction, surveying, roads, structures and estimation.",["Surveying","Construction","Building Materials","Structural Basics","Estimation"],["AutoCAD","Surveying","Quantity Estimation","Site Safety"],["Site Supervisor Trainee","CAD Technician","Survey Technician","Civil Technician"],["B.Tech lateral entry Civil","Construction certifications","Apprenticeship"]),
"Diploma in Mechanical Engineering": D("Practical mechanical training in machines, manufacturing, CAD and maintenance.",["Engineering Drawing","Manufacturing","Thermodynamics","Machine Design","Workshop Practice"],["AutoCAD","CNC Basics","Maintenance","3D CAD"],["Mechanical Technician","CAD Trainee","Production Technician","Maintenance Trainee"],["B.Tech lateral entry Mechanical","Apprenticeship","CAD/CNC certifications"]),
"Diploma in Automobile Engineering": D("Focuses on vehicle systems, servicing, manufacturing and modern EV basics.",["Automobile Systems","Engines","Vehicle Electronics","Workshop Practice","EV Basics"],["Diagnostics","CAD","Vehicle Maintenance","EV Basics"],["Automobile Technician","Service Advisor","EV Technician Trainee"],["B.Tech lateral entry Automobile/Mechanical","EV certifications","Apprenticeship"]),
"Diploma in Chemical Engineering": D("Introduces industrial chemical processes, plant operations, safety and quality control.",["Process Calculations","Chemical Technology","Fluid Flow","Heat Transfer","Safety"],["Process Operations","Safety","Quality Testing","Plant Basics"],["Process Technician","Production Technician","Quality Technician"],["B.Tech lateral entry where available","Process certifications","Apprenticeship"]),
"Diploma in Agricultural Engineering": D("Applies engineering to farm machinery, irrigation, soil-water systems and agricultural processing.",["Farm Machinery","Irrigation","Soil & Water","Processing","Sensors"],["Farm Equipment","Irrigation","Sensors","CAD"],["Agricultural Technician","Irrigation Technician","Agri-Tech Assistant"],["B.Tech Agricultural Engineering","Agri-tech training","Apprenticeship"]),
"Diploma in Biotechnology": D("Practical foundation in biology, laboratory methods, microbiology and biotechnology.",["Biology","Microbiology","Biochemistry","Laboratory Methods","Bioinformatics Basics"],["Lab Skills","Data Recording","Basic Bioinformatics","Safety"],["Lab Technician Trainee","Biotech Assistant","Quality Assistant"],["B.Tech/B.Sc related programs","Lab certifications","Apprenticeship"]),
"Diploma in Food Technology": D("Covers food processing, preservation, quality, packaging and food safety.",["Food Chemistry","Processing","Microbiology","Food Safety","Packaging"],["Quality Testing","Food Safety","Processing","Documentation"],["Food Quality Technician","Production Trainee","Food Lab Assistant"],["B.Tech Food Technology","B.Sc Food Science","Food safety certifications"]),
"Diploma in Textile Technology": D("Training in textile fibers, yarns, fabrics, processing and production.",["Fibers","Yarn","Fabric","Textile Processing","Testing"],["Textile Testing","Production","Quality Control","CAD"],["Textile Technician","Quality Technician","Production Trainee"],["B.Tech Textile Technology","Fashion/Textile degrees","Apprenticeship"]),
"Diploma in Mining Engineering": D("Practical introduction to mine operations, surveying, safety and mineral extraction.",["Mining Methods","Surveying","Mine Safety","Geology Basics","Mineral Processing"],["Surveying","Safety","Mine Planning Basics","CAD/GIS"],["Mining Technician","Survey Technician","Safety Trainee"],["B.Tech Mining","Safety certifications","Apprenticeship"]),
"Diploma in Metallurgy / Materials": D("Studies metals, materials, testing, manufacturing and quality control.",["Metallurgy","Materials Science","Heat Treatment","Testing","Manufacturing"],["Material Testing","Quality Control","Lab Skills","Manufacturing"],["Materials Technician","Quality Technician","Lab Technician"],["B.Tech Metallurgy/Materials","Materials certifications","Apprenticeship"]),
"Diploma in Mechatronics": D("Combines mechanical systems, electronics, sensors, PLCs and automation.",["Mechanics","Electronics","Sensors","PLC","Automation"],["PLC Basics","CAD","Sensors","Maintenance"],["Automation Technician","Mechatronics Technician","Maintenance Trainee"],["B.Tech Mechatronics/Mechanical/EEE","Automation certifications","Apprenticeship"]),
"Diploma in Instrumentation & Control": D("Focuses on industrial measurement, sensors, control systems and automation.",["Sensors","Instrumentation","Control Systems","Process Measurement","PLC"],["Calibration","PLC","Sensors","Troubleshooting"],["Instrumentation Technician","Control Technician","Automation Trainee"],["B.Tech Instrumentation/ECE/EEE","PLC certifications","Apprenticeship"]),
"Diploma in Biomedical Engineering": D("Introduces medical equipment, electronics, sensors and maintenance of healthcare devices.",["Biomedical Instrumentation","Electronics","Medical Devices","Sensors","Safety"],["Equipment Testing","Electronics","Documentation","Maintenance"],["Biomedical Technician","Medical Equipment Technician","Service Trainee"],["B.Tech Biomedical/related","Medical equipment certifications"]),
"Diploma in Architecture Assistantship": D("Practical architectural drafting, building drawings, CAD and basic construction knowledge.",["Architectural Drawing","Building Materials","CAD","Building Services","Estimation"],["AutoCAD","Drafting","3D Modeling","Drawing Reading"],["CAD Technician","Architectural Assistant Trainee","Drafting Technician"],["B.Arch eligibility depends on rules","Architecture-related degree/diploma","CAD certifications"]),
"Diploma in Commercial Practice": D("Develops office, business, accounting, typing, documentation and communication skills.",["Office Management","Accounting Basics","Business Communication","Computer Applications","Typing"],["MS Office","Excel","Documentation","Communication"],["Office Assistant","Accounts Assistant","Data Entry Operator","Administrative Assistant"],["B.Com/BBA","Skill certifications","Apprenticeship"]),
}

# ============================================================
# INTERMEDIATE + ITI/VOCATIONAL
# ============================================================
INTERMEDIATE = {
"MPC": {
    "icon":"📐",
    "subjects":["Mathematics","Physics","Chemistry"],
    "courses":["B.Tech / B.E.","B.Sc Mathematics / Physics / Chemistry","BCA","B.Sc Computer Science / Data Science","B.Sc Artificial Intelligence","Other technology and science degrees"],
    "skills":["Mathematics & Logical Reasoning","Python / Programming","Problem Solving","Statistics","Data Analysis","Communication"],
    "projects":["Student Performance Predictor","Career Recommendation System","College Management Website","AI Chatbot","Data Analysis Dashboard"],
    "internships":["Software Intern","Data Analyst Intern","AI/ML Intern","Web Developer Intern","Research Intern"],
    "careers":["Software Developer","Data Analyst","Data Scientist","AI/ML Engineer","Web Developer","Researcher","Cyber Security Analyst"],
    "higher":["B.Tech → M.Tech → PhD","B.Tech → MS → PhD","B.Sc → M.Sc → PhD","BCA → MCA → Higher Studies"],
    "specializations":["CSE","Computer Science & Data Science (CSD)","Computer Science & Machine Learning (CSM)","Artificial Intelligence & Machine Learning","Data Science","Cyber Security","Information Technology","Internet of Things","Robotics & Automation","Prompt Engineering & Generative AI","ECE","EEE","Mechanical","Civil","Chemical","Agricultural Engineering","Biotechnology","Food Technology","Textile Technology","Aerospace / Aeronautical","Automobile","Industrial Engineering","Mining Engineering","Marine Engineering","Biomedical Engineering","Environmental Engineering","Energy Engineering","Avionics","Materials Engineering"]
},
"BiPC": {
    "icon":"🧬",
    "subjects":["Biology","Physics","Chemistry"],
    "courses":["MBBS","BDS","BAMS","BHMS","B.Pharm","Pharm.D","B.Sc Nursing","B.Sc Biotechnology","B.Sc Microbiology","B.Sc Biochemistry","B.Sc Agriculture","B.Sc Horticulture","B.Sc Food Science / Food Technology","B.Sc Nutrition & Dietetics","BPT / Physiotherapy","B.Sc Medical Laboratory Technology","B.Sc Forensic Science","B.Sc Zoology","B.Sc Botany","B.Sc Life Sciences"],
    "skills":["Biology & Life Sciences","Laboratory Skills","Observation","Data Recording","Basic Statistics","Scientific Communication","Research Skills"],
    "projects":["Plant Growth Study","Water Quality Testing","Food Quality Study","Microbiology Observation","Health Data Analysis","Biodiversity Survey"],
    "internships":["Biotechnology Intern","Laboratory Intern","Pharmacy Intern","Food Technology Intern","Agriculture Intern","Research Intern","Healthcare / Clinical Training where applicable"],
    "careers":["Doctor","Dentist","Pharmacist","Nurse","Physiotherapist","Biotechnologist","Microbiologist","Food Technologist","Agriculture Professional","Lab Technician","Research Assistant","Nutrition Professional"],
    "higher":["M.Tech / M.E. in Biotechnology-related fields where eligible","M.Sc Biotechnology","M.Sc Microbiology","M.Sc Biochemistry","M.Sc Life Sciences","M.Sc Food Science","M.Sc Nutrition","M.Pharm / Pharm.D higher studies","MD/MS after MBBS as applicable","PhD / Research"]
},
"MEC": {
    "icon":"💼",
    "subjects":["Mathematics","Economics","Commerce"],
    "courses":["B.Com","B.Com Computer Applications","BBA","BCA where eligible","BA Economics","B.Sc Economics / Statistics where eligible","Finance and Banking degrees","Business Analytics / Analytics-related programs","CA / CMA / CS professional pathways"],
    "skills":["Accounting","Financial Mathematics","Economics","Excel","Data Analysis","Business Communication","Presentation","Basic SQL / Analytics"],
    "projects":["Personal Finance Dashboard","College Budget Analysis","Sales Dashboard","Business Profit Analysis","Stock / Market Data Analysis project"],
    "internships":["Finance Intern","Accounting Intern","Business Analyst Intern","Banking Intern","Data / Business Analytics Intern","Marketing Intern"],
    "careers":["Accountant","Financial Analyst","Business Analyst","Banking Professional","Business Development Executive","Data / BI Analyst","Economist","Tax / Audit Professional"],
    "higher":["M.Com","MBA Finance","MBA Business Analytics","M.Sc Economics / Applied Economics","M.Sc Finance","M.Com Accounting / Finance","Professional CA / CMA / CS pathways","MS Finance / Business Analytics where eligible","PhD in Commerce / Economics / Management"]
},
"CEC": {
    "icon":"🏛️",
    "subjects":["Civics","Economics","Commerce"],
    "courses":["B.Com","B.Com Computer Applications","BBA","BA","BA Economics","BA Political Science","BA Public Administration","LL.B / Law pathway","Journalism & Mass Communication","Social Sciences","Hotel / Event / Management programs"],
    "skills":["Communication","Accounting Basics","Economics","Public Speaking","Writing","Presentation","Leadership","Digital Skills"],
    "projects":["College Event Management Plan","Local Business Survey","Public Awareness Campaign","Student Budget Project","Community Survey Dashboard"],
    "internships":["Business Intern","Accounting Intern","HR Intern","Marketing Intern","Content / Media Intern","NGO / Social Research Intern","Legal Internship where eligible"],
    "careers":["Business Executive","Accountant","HR Executive","Marketing Executive","Journalist / Content Professional","Public Administration Roles","Legal Professional after required law qualification","Social Research Assistant","Entrepreneur"],
    "higher":["M.Com","MBA","MA Economics","MA Political Science","MA Public Administration","LL.B / LL.M pathway","MA Journalism / Mass Communication","MS Management / Business-related programs where eligible","PhD in Commerce / Economics / Social Sciences"]
},
"HEC": {
    "icon":"🏛️",
    "subjects":["History","Economics","Civics"],
    "courses":["BA History","BA Economics","BA Political Science","BA Public Administration","BA Sociology","BA Psychology","BA Journalism & Mass Communication","BA Social Work","LL.B / Law pathway","Civil Services preparation pathway","Travel & Tourism / Public Administration related degrees"],
    "skills":["History & Research","Critical Thinking","Writing","Public Speaking","Current Affairs","Data Interpretation","Communication","Social Research"],
    "projects":["Local History Documentation","Community Survey","Public Policy Presentation","Historical Timeline Website","Civic Awareness Campaign","Economic Survey Project"],
    "internships":["Research Intern","Content / Journalism Intern","NGO Intern","Public Policy / Social Research Intern","History / Museum-related Internship","Administrative Internship"],
    "careers":["Teacher / Lecturer after required qualifications","Research Assistant","Journalist","Content Writer","Public Administration Professional","Social Researcher","Policy Research Assistant","NGO Professional","Civil Services aspirant / public-sector pathway"],
    "higher":["MA History","MA Economics","MA Political Science","MA Public Administration","MA Sociology","MA Psychology","MA Journalism / Mass Communication","MS Social Research / related programs where eligible","LL.B / LL.M pathway","PhD / Research"]
},
"Humanities / Arts": {
    "icon":"🎨",
    "subjects":["Languages","History","Political Science","Sociology / Psychology / Economics depending on combination"],
    "courses":["BA English / Languages","BA History","BA Political Science","BA Sociology","BA Psychology","BA Journalism & Mass Communication","BA Fine Arts / Design where eligible","BA Social Work","Law","Education / Teaching pathways","Fashion / Interior / Creative Design programs"],
    "skills":["Writing","Communication","Research","Creative Thinking","Presentation","Design Basics","Social Awareness","Critical Thinking"],
    "projects":["Digital Magazine","Short Documentary","Community Survey","Portfolio Website","Local Culture Documentation","Social Awareness Campaign"],
    "internships":["Content Writing Intern","Journalism Intern","Social Media Intern","NGO Intern","Research Intern","Design Intern","Education / Teaching Assistant"],
    "careers":["Writer","Journalist","Teacher / Lecturer after required qualifications","Designer","Psychology-related roles after required higher study","Social Researcher","Content Creator","HR / Communication Professional","Civil Services / Public Administration pathway"],
    "higher":["MA in chosen subject","MS in related social science / humanities fields where eligible","MBA","Journalism / Mass Communication higher studies","LL.B / LL.M pathway","MFA / Design higher studies","B.Ed / M.Ed teaching pathway","PhD / Research"]
}
}

ITI = {
"Electrician":("Electrical wiring, circuits, machines and maintenance.","Electrical Technician / Maintenance / Apprentice"),
"Fitter":("Workshop fitting, tools, machines and mechanical assembly.","Fitter / Maintenance Technician / Apprentice"),
"Welder":("Welding processes, fabrication and workshop safety.","Welder / Fabrication Technician / Apprentice"),
"COPA":("Computer Operator and Programming Assistant: office software, internet, basic programming and data entry.","Computer Operator / Data Entry / IT Support Trainee"),
"Electronics Mechanic":("Electronic circuits, testing, repair and equipment maintenance.","Electronics Technician / Service Technician"),
"Mechanic Motor Vehicle":("Vehicle servicing, diagnostics and maintenance.","Automobile Technician / Service Technician"),
"Refrigeration & AC":("Refrigeration, air-conditioning systems and servicing.","AC Technician / Refrigeration Technician"),
"Plumber":("Pipe fitting, water systems and maintenance.","Plumber / Maintenance Technician"),
"Draughtsman Civil":("Civil drafting, CAD and building drawings.","CAD Technician / Drafting Assistant"),
"Draughtsman Mechanical":("Mechanical drawings, CAD and manufacturing drawings.","CAD Technician / Drafting Assistant"),
"Turner":("Lathe operations, machining and workshop practice.","Machine Operator / Turner"),
"Machinist":("Machine tools, machining operations and production.","Machinist / Production Trainee"),
"Solar Technician":("Solar PV installation, basic electrical work and maintenance.","Solar Technician / Renewable Energy Trainee"),
"Singing / Vocal Music":("A creative vocational pathway focused on vocal training, performance and music practice. Availability varies by institute.","Singer / Performer / Music Content Creator"),
"Dancing / Performing Arts":("Skill-based training in dance, stage performance and choreography. Availability varies by institute.","Dancer / Choreographer / Performer"),
"Acting / Theatre":("Performance, theatre practice, voice, expression and stage skills. Availability varies by institute.","Actor / Theatre Artist / Content Performer"),
"Drawing / Visual Arts":("Drawing, illustration and visual creativity. Availability varies by institute.","Artist / Illustrator / Design Assistant"),
"Photography":("Camera basics, composition, editing and visual storytelling. Availability varies by institute.","Photographer / Photo Editor / Content Creator"),
"Fashion Design":("Garment design, textiles, styling and basic fashion production. Availability varies by institute.","Fashion Assistant / Designer Trainee / Stylist Assistant"),
"Beauty & Wellness":("Beauty care, grooming, wellness and salon skills. Availability varies by institute.","Beauty Professional / Salon Assistant / Wellness Assistant"),
"Culinary / Baking":("Food preparation, kitchen practice, baking and food presentation. Availability varies by institute.","Cook / Baker / Kitchen Assistant"),
"Digital Content Creation":("Video, social media, basic editing, design and content production. Availability varies by institute.","Content Creator / Video Editor / Social Media Assistant"),
}

# ============================================================
# LOGIN + EMAIL OTP VERIFICATION
# ============================================================
# For real email delivery, add SMTP settings to .streamlit/secrets.toml:
# SMTP_HOST = "smtp.gmail.com"
# SMTP_PORT = 587
# SMTP_USERNAME = "yourprojectemail@gmail.com"
# SMTP_PASSWORD = "your-16-character-gmail-app-password"
# SMTP_FROM = "yourprojectemail@gmail.com"
#
# IMPORTANT: SMTP_PASSWORD is an APP PASSWORD, not the user's email password.
# Never put SMTP credentials directly into this Python file.

DB_FILE = "futurepath_users.db"


def init_user_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def valid_email(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()))


def register_user(email, password):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(
            "INSERT INTO users(email,password_hash,created_at) VALUES(?,?,?)",
            (email.lower().strip(), hash_password(password), datetime.now().isoformat())
        )
        conn.commit()
        return True, "Registration successful. You can now request an OTP."
    except sqlite3.IntegrityError:
        return False, "This email is already registered. Please login instead."
    finally:
        conn.close()


def check_password(email, password):
    conn = sqlite3.connect(DB_FILE)
    row = conn.execute(
        "SELECT password_hash FROM users WHERE email=?",
        (email.lower().strip(),)
    ).fetchone()
    conn.close()
    return row is not None and row[0] == hash_password(password)


def send_otp_email(to_email, otp):
    """DEMO MODE: no real email is sent; OTP is displayed in the app."""
    return True, "DEMO MODE: OTP generated. No real email is sent."


init_user_db()

for key, value in {
    "authenticated": False,
    "otp": None,
    "otp_expires": None,
    "otp_email": "",
    "login_user": "",
    "auth_mode": "Login",
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

if not st.session_state.authenticated:
    st.markdown(
        '<div class="hero"><h1>🌈 FuturePath</h1>'
        '<h2>Your Career. Your Future. Your Path. 🚀</h2>'
        '<p>Secure email verification to enter FuturePath</p></div>',
        unsafe_allow_html=True
    )

    st.subheader("🔐 FuturePath Account")
    mode = st.radio("", ["Login", "Register"], horizontal=True, key="auth_mode")

    if mode == "Register":
        st.info("Create your FuturePath account using your email and your own password. Your password is never displayed or stored as plain text.")
        email = st.text_input("📧 Register Email", placeholder="you@example.com")
        password = st.text_input("🔑 Create Password", type="password", placeholder="Create your password")
        confirm = st.text_input("🔑 Confirm Password", type="password", placeholder="Re-enter your password")

        if st.button("📝 Create Account", use_container_width=True):
            if not valid_email(email):
                st.error("Please enter a valid email address.")
            elif len(password) < 6:
                st.error("Password must contain at least 6 characters.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                ok, message = register_user(email, password)
                if ok:
                    st.success(message)
                    st.info("Now select Login, enter the same email and your original password, then request the OTP.")
                else:
                    st.error(message)

    else:
        st.write("Enter the email and password you registered with. The password field is masked and is never displayed.")
        email = st.text_input("📧 Registered Email", placeholder="Enter your registered email")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter your original password")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("📨 Send OTP to My Email", use_container_width=True):
                if not valid_email(email):
                    st.error("Please enter a valid registered email address.")
                elif not check_password(email, password):
                    st.error("Email or password is incorrect. Use the password you created during registration.")
                else:
                    otp = f"{random.randint(0, 999999):06d}"
                    ok, message = send_otp_email(email.strip(), otp)
                    st.info(f"🧪 DEMO OTP: **{otp}**")
                    st.caption("Demo verification only — no email is sent.")
                    if ok:
                        st.session_state.otp = otp
                        st.session_state.otp_email = email.strip().lower()
                        st.session_state.otp_expires = datetime.now() + timedelta(minutes=10)
                        st.success(message)
                    else:
                        st.error(message)

        with c2:
            otp_input = st.text_input("🔢 Enter Email OTP", max_chars=6, placeholder="6-digit code")

        if st.button("✅ Verify OTP & Login", use_container_width=True):
            if not st.session_state.otp:
                st.error("First click 'Send OTP to My Email'.")
            elif email.strip().lower() != st.session_state.otp_email:
                st.error("Please use the same registered email to which the OTP was sent.")
            elif datetime.now() > st.session_state.otp_expires:
                st.error("This OTP has expired. Please request a new OTP.")
                st.session_state.otp = None
            elif otp_input.strip() != st.session_state.otp:
                st.error("Incorrect OTP. Please check your registered email.")
            else:
                st.session_state.authenticated = True
                st.session_state.login_user = email.strip().lower()
                st.session_state.otp = None
                st.session_state.otp_email = ""
                st.session_state.otp_expires = None
                st.success("Email verified successfully. Welcome to FuturePath! 🎉")
                st.rerun()

    st.caption("🔒 Passwords are stored as hashes. OTPs are sent to the registered email and expire after 10 minutes.")
    st.stop()

# ============================================================
# STATE + HELPERS
# ============================================================
for k,v in {"page":"home","selected_branch":None,"selected_stream":None,"selected_diploma":None,"selected_iti":None}.items():
    if k not in st.session_state: st.session_state[k]=v

def go(page): st.session_state.page=page; st.rerun()
def branch(name): st.session_state.selected_branch=name; st.session_state.page="branch"; st.rerun()
def diploma(name): st.session_state.selected_diploma=name; st.session_state.page="diploma"; st.rerun()
def stream(name): st.session_state.selected_stream=name; st.session_state.page="stream"; st.rerun()
def iti(name): st.session_state.selected_iti=name; st.session_state.page="iti_detail"; st.rerun()

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown("## 🌈 FuturePath")
st.sidebar.caption("Your Career • Your Future • Your Path")

LANG={
"English":{"home":"Home","roadmap":"Start After Class 10","inter":"Intermediate","diploma":"Polytechnic / Diploma","iti":"ITI / Vocational","eng":"Engineering Branches","skills":"Skills","projects":"Projects","intern":"Internships","careers":"Careers","quiz":"Career Quiz","help":"Help Desk","ai":"AI Assistant","logout":"Logout","language":"Language","back":"← Back","subjects":"Subjects","skills2":"Skills","projects2":"Projects","intern2":"Internship Roles","careers2":"Career Options","mtech":"M.Tech Courses after B.Tech","ms":"MS Courses after B.Tech","note":"Course names and availability vary by university/institute. Check the specific institution before applying."},
"Telugu":{"home":"హోమ్","roadmap":"10వ తరగతి తర్వాత ప్రారంభం","inter":"ఇంటర్మీడియట్","diploma":"పాలిటెక్నిక్ / డిప్లొమా","iti":"ITI / వొకేషనల్","eng":"ఇంజినీరింగ్ బ్రాంచ్‌లు","skills":"స్కిల్స్","projects":"ప్రాజెక్టులు","intern":"ఇంటర్న్‌షిప్స్","careers":"కెరీర్స్","quiz":"కెరీర్ క్విజ్","help":"హెల్ప్ డెస్క్","ai":"AI అసిస్టెంట్","logout":"లాగ్ అవుట్","language":"భాష","back":"← వెనక్కి","subjects":"సబ్జెక్ట్స్","skills2":"స్కిల్స్","projects2":"ప్రాజెక్టులు","intern2":"ఇంటర్న్‌షిప్ పాత్రలు","careers2":"కెరీర్ అవకాశాలు","mtech":"B.Tech తర్వాత M.Tech కోర్సులు","ms":"B.Tech తర్వాత MS కోర్సులు","note":"కోర్సుల పేర్లు మరియు లభ్యత యూనివర్సిటీ/ఇన్‌స్టిట్యూట్‌ను బట్టి మారవచ్చు."},
"Hindi":{"home":"होम","roadmap":"कक्षा 10 के बाद शुरू करें","inter":"इंटरमीडिएट","diploma":"पॉलिटेक्निक / डिप्लोमा","iti":"ITI / वोकेशनल","eng":"इंजीनियरिंग शाखाएँ","skills":"स्किल्स","projects":"प्रोजेक्ट्स","intern":"इंटर्नशिप","careers":"करियर","quiz":"करियर क्विज़","help":"हेल्प डेस्क","ai":"AI असिस्टेंट","logout":"लॉग आउट","language":"भाषा","back":"← वापस","subjects":"विषय","skills2":"स्किल्स","projects2":"प्रोजेक्ट्स","intern2":"इंटर्नशिप भूमिकाएँ","careers2":"करियर विकल्प","mtech":"B.Tech के बाद M.Tech कोर्स","ms":"B.Tech के बाद MS कोर्स","note":"कोर्स और उपलब्धता विश्वविद्यालय/संस्थान के अनुसार बदल सकती है।"},
"Tamil":{"home":"முகப்பு","roadmap":"10ஆம் வகுப்புக்குப் பிறகு தொடங்கு","inter":"இடைநிலை","diploma":"பாலிடெக்னிக் / டிப்ளமா","iti":"ITI / தொழில்நுட்பம்","eng":"பொறியியல் பிரிவுகள்","skills":"திறன்கள்","projects":"திட்டங்கள்","intern":"இன்டர்ன்ஷிப்","careers":"வேலைவாய்ப்புகள்","quiz":"கேரியர் வினாடி வினா","help":"உதவி மையம்","ai":"AI உதவியாளர்","logout":"வெளியேறு","language":"மொழி","back":"← பின்செல்","subjects":"பாடங்கள்","skills2":"திறன்கள்","projects2":"திட்டங்கள்","intern2":"இன்டர்ன்ஷிப் பணிகள்","careers2":"வேலை வாய்ப்புகள்","mtech":"B.Tech பிறகு M.Tech படிப்புகள்","ms":"B.Tech பிறகு MS படிப்புகள்","note":"படிப்பு பெயர்கள் மற்றும் கிடைக்கும் நிலை பல்கலைக்கழகத்தைப் பொறுத்து மாறலாம்."},
"Kannada":{"home":"ಮುಖಪುಟ","roadmap":"10ನೇ ತರಗತಿಯ ನಂತರ ಪ್ರಾರಂಭಿಸಿ","inter":"ಪಿಯುಸಿ","diploma":"ಪಾಲಿಟೆಕ್ನಿಕ್ / ಡಿಪ್ಲೊಮಾ","iti":"ITI / ವೊಕೇಷನಲ್","eng":"ಎಂಜಿನಿಯರಿಂಗ್ ಶಾಖೆಗಳು","skills":"ಕೌಶಲ್ಯಗಳು","projects":"ಪ್ರಾಜೆಕ್ಟ್‌ಗಳು","intern":"ಇಂಟರ್ನ್‌ಶಿಪ್","careers":"ವೃತ್ತಿಗಳು","quiz":"ಕೆರಿಯರ್ ಕ್ವಿಜ್","help":"ಸಹಾಯ ಕೇಂದ್ರ","ai":"AI ಸಹಾಯಕ","logout":"ಲಾಗ್ ಔಟ್","language":"ಭಾಷೆ","back":"← ಹಿಂದೆ","subjects":"ವಿಷಯಗಳು","skills2":"ಕೌಶಲ್ಯಗಳು","projects2":"ಪ್ರಾಜೆಕ್ಟ್‌ಗಳು","intern2":"ಇಂಟರ್ನ್‌ಶಿಪ್ ಪಾತ್ರಗಳು","careers2":"ವೃತ್ತಿ ಆಯ್ಕೆಗಳು","mtech":"B.Tech ನಂತರ M.Tech ಕೋರ್ಸ್‌ಗಳು","ms":"B.Tech ನಂತರ MS ಕೋರ್ಸ್‌ಗಳು","note":"ಕೋರ್ಸ್‌ಗಳ ಲಭ್ಯತೆ ವಿಶ್ವವಿದ್ಯಾಲಯ/ಸಂಸ್ಥೆಯ ಮೇಲೆ ಅವಲಂಬಿತವಾಗಿರುತ್ತದೆ."},
"Malayalam":{"home":"ഹോം","roadmap":"10-ാം ക്ലാസിന് ശേഷം തുടങ്ങുക","inter":"ഇന്റർമീഡിയറ്റ്","diploma":"പോളിടെക്നിക് / ഡിപ്ലോമ","iti":"ITI / വൊക്കേഷണൽ","eng":"എഞ്ചിനീയറിംഗ് ശാഖകൾ","skills":"സ്കിൽസ്","projects":"പ്രോജക്റ്റുകൾ","intern":"ഇന്റേൺഷിപ്പ്","careers":"കരിയർ","quiz":"കരിയർ ക്വിസ്","help":"ഹെൽപ്പ് ഡെസ്ക്","ai":"AI അസിസ്റ്റന്റ്","logout":"ലോഗ് ഔട്ട്","language":"ഭാഷ","back":"← തിരികെ","subjects":"വിഷയങ്ങൾ","skills2":"സ്കിൽസ്","projects2":"പ്രോജക്റ്റുകൾ","intern2":"ഇന്റേൺഷിപ്പ് റോളുകൾ","careers2":"കരിയർ ഓപ്ഷനുകൾ","mtech":"B.Tech കഴിഞ്ഞുള്ള M.Tech കോഴ്സുകൾ","ms":"B.Tech കഴിഞ്ഞുള്ള MS കോഴ്സുകൾ","note":"കോഴ്സ് ലഭ്യത സർവകലാശാല/സ്ഥാപനം അനുസരിച്ച് മാറാം."},
"Marathi":{"home":"होम","roadmap":"10वी नंतर सुरू करा","inter":"इंटरमिजिएट","diploma":"पॉलिटेक्निक / डिप्लोमा","iti":"ITI / व्यावसायिक","eng":"अभियांत्रिकी शाखा","skills":"कौशल्ये","projects":"प्रकल्प","intern":"इंटर्नशिप","careers":"करिअर","quiz":"करिअर क्विझ","help":"मदत केंद्र","ai":"AI सहाय्यक","logout":"लॉग आउट","language":"भाषा","back":"← मागे","subjects":"विषय","skills2":"कौशल्ये","projects2":"प्रकल्प","intern2":"इंटर्नशिप भूमिका","careers2":"करिअर पर्याय","mtech":"B.Tech नंतरचे M.Tech कोर्स","ms":"B.Tech नंतरचे MS कोर्स","note":"कोर्सची उपलब्धता विद्यापीठ/संस्थेनुसार बदलू शकते."},
"Bengali":{"home":"হোম","roadmap":"দশম শ্রেণির পর শুরু করুন","inter":"ইন্টারমিডিয়েট","diploma":"পলিটেকনিক / ডিপ্লোমা","iti":"ITI / ভোকেশনাল","eng":"ইঞ্জিনিয়ারিং শাখা","skills":"দক্ষতা","projects":"প্রজেক্ট","intern":"ইন্টার্নশিপ","careers":"ক্যারিয়ার","quiz":"ক্যারিয়ার কুইজ","help":"হেল্প ডেস্ক","ai":"AI অ্যাসিস্ট্যান্ট","logout":"লগ আউট","language":"ভাষা","back":"← ফিরে যান","subjects":"বিষয়","skills2":"দক্ষতা","projects2":"প্রজেক্ট","intern2":"ইন্টার্নশিপ ভূমিকা","careers2":"ক্যারিয়ার অপশন","mtech":"B.Tech-এর পর M.Tech কোর্স","ms":"B.Tech-এর পর MS কোর্স","note":"কোর্সের নাম ও প্রাপ্যতা বিশ্ববিদ্যালয়/প্রতিষ্ঠানভেদে পরিবর্তিত হতে পারে।"}
}

if "language" not in st.session_state:
    st.session_state.language="English"
language=st.sidebar.selectbox("🌐 "+LANG[st.session_state.language]["language"],["English","Telugu","Hindi","Tamil","Kannada","Malayalam","Marathi","Bengali"],index=["English","Telugu","Hindi","Tamil","Kannada","Malayalam","Marathi","Bengali"].index(st.session_state.language),key="language_select")
st.session_state.language=language
T=LANG[language]

nav=[("🏠 "+T["home"],"home"),("🗺️ "+T["roadmap"],"roadmap"),("📚 "+T["inter"],"intermediate"),("🛠️ "+T["diploma"],"polytechnic"),("🔧 "+T["iti"],"iti"),("🎓 "+T["eng"],"branches"),("🧠 "+T["skills"],"skills"),("🛠️ "+T["projects"],"projects"),("💼 "+T["intern"],"internships"),("🚀 "+T["careers"],"careers"),("🎯 "+T["quiz"],"quiz"),("🆘 "+T["help"],"helpdesk"),("🤖 "+T["ai"],"ai_assistant")]
for label,page in nav:
    if st.sidebar.button(label,key="nav_"+page,use_container_width=True): go(page)

st.sidebar.markdown("---")
st.sidebar.caption("👤 "+st.session_state.login_user)
if st.sidebar.button("🚪 "+T["logout"],use_container_width=True):
    st.session_state.authenticated=False
    st.session_state.login_user=""
    st.rerun()

# ============================================================
# HOME
# ============================================================
if st.session_state.page=="home":
    st.markdown('<div class="hero"><h1>🌈 FuturePath</h1><h2>Your Career. Your Future. Your Path. 🚀</h2><p>Explore choices after Class 10 → Intermediate / Diploma / ITI → B.Tech → M.Tech / MS → Skills → Projects → Internships → Careers</p></div>',unsafe_allow_html=True)
    q=st.text_input("🔎 Search branch, diploma or career",placeholder="Data Science, CSE, Civil, Diploma, AI...")
    if q:
        hits=[x for x,d in BRANCHES.items() if q.lower() in x.lower() or q.lower() in d["description"].lower() or any(q.lower() in c.lower() for c in d["careers"])]
        hits += [x for x in DIPLOMAS if q.lower() in x.lower()]
        hits=list(dict.fromkeys(hits))
        for i,x in enumerate(hits):
            if x in BRANCHES:
                if st.button(f"{BRANCHES[x]['icon']} {x}",key=f"home_b_{i}",use_container_width=True): branch(x)
            else:
                if st.button(f"🎓 {x}",key=f"home_d_{i}",use_container_width=True): diploma(x)
    st.subheader("🗺️ "+T["roadmap"])
    a,b,c=st.columns(3)
    for col,title,page,desc in [(a,"📚 Intermediate","intermediate","MPC • BiPC • MEC • CEC • Humanities"),(b,"🛠️ Polytechnic / Diploma","polytechnic","Common technical diploma courses with clear information"),(c,"🔧 ITI / Vocational","iti","Technical trades + creative/vocational skill paths")]:
        with col:
            st.markdown(f'<div class="card"><h3>{title}</h3><p>{desc}</p></div>',unsafe_allow_html=True)
            if st.button("Explore →",key="home_"+page,use_container_width=True): go(page)
    st.subheader("🎓 MPC → Engineering → Higher Studies")
    st.info("For MPC students, FuturePath now contains a broad engineering list. Open any branch to see Subjects, Skills, Projects, Internships, Careers, M.Tech options and MS options after B.Tech.")
    if st.button("View all Engineering Branches →",use_container_width=True): go("branches")

# ============================================================
# ROADMAP / INTERMEDIATE
# ============================================================
elif st.session_state.page=="roadmap":
    st.title("🗺️ After Class 10 Roadmap")
    st.write("Class 10 → Choose a pathway → Higher education / skills → Build skills → Projects → Internship → Career or higher studies")
    x,y,z=st.columns(3)
    for col,title,page in [(x,"📚 Intermediate","intermediate"),(y,"🛠️ Diploma","polytechnic"),(z,"🔧 ITI / Vocational","iti")]:
        with col:
            st.subheader(title)
            if st.button("Explore →",key="road_"+page,use_container_width=True): go(page)

elif st.session_state.page=="intermediate":
    st.title("📚 Intermediate Streams")
    cols=st.columns(3)
    for i,(name,d) in enumerate(INTERMEDIATE.items()):
        with cols[i%3]:
            st.subheader(f"{d['icon']} {name}")
            st.write("**Subjects:** "+", ".join(d["subjects"]))
            st.write("**Courses:** "+", ".join(d["courses"][:4]) + (" ..." if len(d["courses"])>4 else ""))
            st.write("**Skills:** "+", ".join(d["skills"][:3]))
            if st.button("Explore →",key="stream_"+str(i),use_container_width=True): stream(name)

elif st.session_state.page=="stream":
    name=st.session_state.selected_stream; d=INTERMEDIATE[name]
    st.title(f"{d['icon']} {name}")
    if st.button(T["back"]): go("intermediate")

    st.info(f"{name} is one of the pathways students can choose after Class 10. Explore the complete education → skills → projects → internship → career → higher-studies path below.")

    st.subheader("📚 Subjects")
    cols=st.columns(3)
    for i,item in enumerate(d["subjects"]):
        with cols[i%3]: st.info(item)

    st.subheader("🎓 Degree / Course Options")
    cols=st.columns(2)
    for i,item in enumerate(d["courses"]):
        with cols[i%2]: st.write("•",item)

    st.subheader("🧠 Skills to Build")
    cols=st.columns(3)
    for i,item in enumerate(d["skills"]):
        with cols[i%3]: st.success(item)

    st.subheader("🛠️ Project Ideas")
    cols=st.columns(2)
    for i,item in enumerate(d["projects"]):
        with cols[i%2]: st.write("•",item)

    st.subheader("💼 Internship Opportunities")
    cols=st.columns(3)
    for i,item in enumerate(d["internships"]):
        with cols[i%3]: st.write("•",item)

    st.subheader("🚀 Career Options")
    cols=st.columns(3)
    for i,item in enumerate(d["careers"]):
        with cols[i%3]: st.write("•",item)

    st.subheader("🎓 Higher Studies")
    for item in d["higher"]: st.write("•",item)

    if name=="MPC":
        st.markdown("---")
        st.subheader("📐 MPC → Engineering Branches")
        st.caption("Branch names and availability vary by college. Prompt Engineering is shown as an emerging specialization/skill pathway; it is not a universally offered standalone B.Tech branch.")
        search_mpc=st.text_input("🔎 Search MPC engineering branch",placeholder="CSE, Data Science, Prompt Engineering, Civil...")
        branch_items=[bn for bn in BRANCHES if not search_mpc or search_mpc.lower() in bn.lower()]
        cols=st.columns(3)
        for i,bn in enumerate(branch_items):
            with cols[i%3]:
                if st.button(f"{BRANCHES[bn]['icon']} {bn}",key="mpc_branch_"+str(i),use_container_width=True): branch(bn)

        st.markdown("---")
        st.subheader("✨ Prompt Engineering & Generative AI")
        st.write("Prompt Engineering can be learned by MPC students through CSE, AI/ML, Data Science or related B.Tech programs, electives, projects and certifications. It focuses on designing, testing and evaluating prompts and AI workflows.")
        p=BRANCHES.get("Prompt Engineering & Generative AI")
        if p:
            pc1,pc2=st.columns(2)
            with pc1:
                st.write("**Key subjects:** "+", ".join(p["subjects"]))
                st.write("**Skills:** "+", ".join(p["skills"]))
            with pc2:
                st.write("**Projects:** "+", ".join(p["projects"]))
                st.write("**Careers:** "+", ".join(p["careers"]))
            if st.button("Explore Prompt Engineering complete path →",key="mpc_prompt",use_container_width=True): branch("Prompt Engineering & Generative AI")

# ============================================================
# DIPLOMA
# ============================================================
elif st.session_state.page=="polytechnic":
    st.title("🛠️ Polytechnic / Diploma — Common Courses")
    st.write("Each course below includes what you study, skills, career roles and further-study options.")
    q=st.text_input("🔎 Search diploma",placeholder="Computer, Civil, Mechanical, Food...")
    items=[x for x in DIPLOMAS if not q or q.lower() in x.lower()]
    st.write(f"**{len(items)} courses shown**")
    cols=st.columns(3)
    for i,x in enumerate(items):
        with cols[i%3]:
            st.subheader("🎓 "+x)
            st.write(DIPLOMAS[x]["description"])
            if st.button("View complete information →",key="dip_"+str(i),use_container_width=True): diploma(x)

elif st.session_state.page=="diploma":
    name=st.session_state.selected_diploma; d=DIPLOMAS[name]
    st.title("🎓 "+name)
    if st.button(T["back"]): go("polytechnic")
    st.write(d["description"])
    st.subheader(T["subjects"]); [st.write("•",x) for x in d["subjects"]]
    st.subheader("🧠 "+T["skills2"]); [st.write("•",x) for x in d["skills"]]
    st.subheader("🚀 "+T["careers2"]); [st.write("•",x) for x in d["careers"]]
    st.subheader("🎓 Further Study / Next Steps"); [st.write("•",x) for x in d["further"]]

# ============================================================
# ITI
# ============================================================
elif st.session_state.page=="iti":
    st.title("🔧 ITI / Vocational")
    st.info("The first group contains common technical trades. Creative options such as singing and dancing are shown as vocational/skill pathways; they are not necessarily official ITI trades in every institute.")
    q=st.text_input("🔎 Search trade / skill")
    items=[x for x in ITI if not q or q.lower() in x.lower()]
    cols=st.columns(3)
    for i,x in enumerate(items):
        with cols[i%3]:
            st.subheader("🔧 "+x)
            st.write(ITI[x][0])
            if st.button("Learn more →",key="iti_"+str(i),use_container_width=True): iti(x)

elif st.session_state.page=="iti_detail":
    name=st.session_state.selected_iti; desc,career=ITI[name]
    st.title("🔧 "+name)
    if st.button(T["back"]): go("iti")
    st.write(desc)
    st.subheader("🚀 Typical Path")
    st.write("Training → Practice → Portfolio / Apprenticeship → Work or Further Training")
    st.subheader("💼 Possible Roles")
    st.write(career)

# ============================================================
# ENGINEERING BRANCH LIST + DETAILS
# ============================================================
elif st.session_state.page=="branches":
    st.title("🎓 MPC → Engineering Branches")
    st.write("Choose a branch to see its complete B.Tech → M.Tech / MS pathway.")
    q=st.text_input("🔎 Search engineering branch",placeholder="CSE, Data Science, ECE, Civil...")
    cats=sorted(set(d["category"] for d in BRANCHES.values()))
    cat=st.selectbox("📂 Filter category",["All"]+cats)
    items=[x for x,d in BRANCHES.items() if (cat=="All" or d["category"]==cat) and (not q or q.lower() in x.lower() or q.lower() in d["description"].lower())]
    st.write(f"**{len(items)} branches found**")
    cols=st.columns(3)
    for i,x in enumerate(items):
        with cols[i%3]:
            st.subheader(f"{BRANCHES[x]['icon']} {x}")
            st.caption(BRANCHES[x]["category"])
            st.write(BRANCHES[x]["description"])
            if st.button("View complete path →",key="eng_"+str(i),use_container_width=True): branch(x)

elif st.session_state.page=="branch":
    name=st.session_state.selected_branch; d=BRANCHES[name]
    st.title(f"{d['icon']} {name}")
    st.caption(d["category"])
    if st.button(T["back"]): go("branches")
    st.write(d["description"])
    st.success(f"B.Tech / B.E. → Skills → Projects → Internship → Career / Higher Studies")
    tabs=st.tabs(["Overview",T["subjects"],T["skills2"],T["projects2"],T["intern2"],T["careers2"],T["mtech"],T["ms"]])
    with tabs[0]:
        st.subheader("🎓 Education Path")
        st.write("Class 10 → MPC → B.Tech / B.E. → Skills → Projects → Internship → Job or M.Tech / MS")
        st.info(T["note"])
    with tabs[1]:
        for x in d["subjects"]: st.write("•",x)
    with tabs[2]:
        for x in d["skills"]: st.write("•",x)
    with tabs[3]:
        for x in d["projects"]: st.write("•",x)
    with tabs[4]:
        for x in d["internships"]: st.write("•",x)
    with tabs[5]:
        for x in d["careers"]: st.write("•",x)
    with tabs[6]:
        st.info("These are common/relevant M.Tech specializations. A university may use a different title or may not offer every specialization.")
        for x in d["mtech"]: st.write("•",x)
    with tabs[7]:
        st.info("These are common/relevant MS specializations. Exact names and eligibility vary by university and country.")
        for x in d["ms"]: st.write("•",x)

# ============================================================
# GENERAL PAGES
# ============================================================
elif st.session_state.page=="skills":
    st.title("🧠 "+T["skills"]+" Explorer")
    groups={"💻 Programming":["Python","Java","C/C++","JavaScript","SQL"],"📊 Data & Analytics":["Excel","SQL","Statistics","Pandas","NumPy","Power BI"],"🤖 AI/ML":["Machine Learning","Deep Learning","NLP","Computer Vision","Generative AI"],"🌐 Technology":["Web Development","Cloud","Git","Linux","Networking"],"⚙️ Engineering":["CAD","Electronics","Manufacturing","Control Systems","Thermodynamics"],"💬 Soft Skills":["Communication","Teamwork","Problem Solving","Presentation","Time Management"]}
    cols=st.columns(3)
    for i,(g,items) in enumerate(groups.items()):
        with cols[i%3]:
            st.subheader(g)
            for x in items: st.write("•",x)

elif st.session_state.page=="projects":
    st.title("🛠️ "+T["projects"]+"")
    for level,items in {"🌱 Beginner":["Student Registration System","Marks Calculator","Portfolio Website","Expense Tracker"],"🚀 Intermediate":["Placement Dashboard","Student Performance Predictor","Hospital Data Analysis","Smart Attendance System"],"🔥 Advanced":["AI Career Guidance System","Internship Matching System","Real-Time Analytics Dashboard","AI Student Support System"]}.items():
        st.subheader(level)
        for x in items: st.write("•",x)

elif st.session_state.page=="internships":
    st.title("💼 "+T["intern"]+" Explorer")
    selected=st.selectbox("Choose a branch",list(BRANCHES.keys()))
    d=BRANCHES[selected]
    for x in d["internships"]: st.write("•",x)
    st.info("Build 2–3 relevant projects, maintain GitHub/portfolio evidence and prepare a simple one-page resume.")

elif st.session_state.page=="careers":
    st.title("🚀 "+T["careers"]+" Explorer")
    q=st.text_input("🔎 Search career")
    seen=set(); rows=[]
    for b,d in BRANCHES.items():
        for c in d["careers"]:
            if c not in seen and (not q or q.lower() in c.lower()): rows.append((c,b)); seen.add(c)
    cols=st.columns(3)
    for i,(c,b) in enumerate(rows):
        with cols[i%3]:
            st.subheader("🚀 "+c); st.caption("Branch: "+b)
            if st.button("Explore branch →",key="career_"+str(i),use_container_width=True): branch(b)

elif st.session_state.page=="helpdesk":
    st.title("🆘 "+T["help"]+"")
    st.write("Welcome to the FuturePath Help Desk. Use this section when you need guidance about the website, education paths, branches, diplomas or career planning.")

    topic=st.selectbox("What do you need help with?",[
        "Using FuturePath",
        "After Class 10",
        "Intermediate Streams",
        "Engineering Branches",
        "M.Tech / MS after B.Tech",
        "Polytechnic / Diploma",
        "ITI / Vocational",
        "Skills / Projects",
        "Internships",
        "Careers"
    ])

    HELP={
        "Using FuturePath":"Use the sidebar to move between Home, Intermediate, Diploma, ITI, Engineering, Skills, Projects, Internships, Careers, Quiz, Help Desk and AI Assistant.",
        "After Class 10":"Explore Intermediate, Polytechnic/Diploma and ITI/Vocational pathways. Compare subjects, courses, skills and future options.",
        "Intermediate Streams":"Open a stream to see subjects, degree/course options, skills, projects, internships, careers and higher studies.",
        "Engineering Branches":"Open an engineering branch to see B.Tech subjects, skills, projects, internships, careers and relevant M.Tech/MS pathways.",
        "M.Tech / MS after B.Tech":"Open any engineering branch and use the M.Tech Courses after B.Tech and MS Courses after B.Tech tabs. Exact offerings and eligibility vary by university.",
        "Polytechnic / Diploma":"Select a diploma to see its description, subjects, skills, career roles and further-study options.",
        "ITI / Vocational":"Explore technical ITI trades as well as the creative vocational pathways listed in FuturePath. Availability varies by institute.",
        "Skills / Projects":"Use the Skills and Projects pages to identify skills to learn and project ideas to build a portfolio.",
        "Internships":"Choose a branch in Internship Explorer to see related internship roles. Build projects and a simple resume before applying.",
        "Careers":"Search careers and open the related branch to understand the education and skill pathway."
    }
    st.info(HELP[topic])

    st.subheader("📩 Common Questions")
    with st.expander("How do I choose a branch?"):
        st.write("Compare subjects, skills, projects, internship roles, career options and higher-study pathways. Also check eligibility, fees, location and the actual curriculum of the institutions you are considering.")
    with st.expander("Where can I see M.Tech and MS options?"):
        st.write("Open Engineering Branches → select a branch → use the M.Tech and MS tabs.")
    with st.expander("Can I use the AI Assistant?"):
        st.write("Yes. Open 🤖 AI Assistant from the sidebar and ask a career-path question.")

elif st.session_state.page=="ai_assistant":
    # --------------------------------------------------------
    # Conversational FuturePath AI Assistant
    # The greeting, prompts and common replies follow the
    # language selected in the sidebar.
    # --------------------------------------------------------
    AI_LANG = {
        "English": {
            "title": "🤖 FuturePath AI Assistant",
            "welcome": "Hi! 👋 How can I help you with your education and career path today?",
            "placeholder": "Type your message...",
            "send": "Send",
            "clear": "Clear conversation",
            "typing": "FuturePath AI",
            "suggest": "✨ Try asking",
            "empty": "Please type a message first.",
            "fallback": "I can help with Class 10 pathways, intermediate streams, engineering branches, diploma, ITI/vocational options, skills, projects, internships, careers and M.Tech/MS pathways.",
            "greeting": "Hi! 👋 I'm FuturePath AI. How can I help you?",
            "mpc": "After MPC, you can explore B.Tech/B.E., B.Sc and other science/technology pathways. For engineering, FuturePath includes CSE, CSD, CSM, AI & ML, Data Science, Cyber Security, IT, ECE, EEE and other branches.",
            "intern": "You can prepare for internships by learning relevant skills, building 2–3 projects, keeping your work on GitHub/portfolio and preparing a simple resume.",
            "project": "Open Projects to explore beginner, intermediate and advanced ideas. You can also open an engineering branch to see branch-specific projects.",
            "skill": "Open Skills to explore programming, data analytics, AI/ML, technology, engineering and soft skills.",
            "career": "Open Careers to search career roles and then explore the related branch and pathway.",
            "diploma": "Open Polytechnic / Diploma to explore diploma courses, subjects, skills, careers and further-study options.",
            "mtech": "Open an engineering branch and select the M.Tech tab to see common relevant M.Tech pathways after B.Tech.",
            "ms": "Open an engineering branch and select the MS tab to see common relevant MS pathways after B.Tech. Exact programs vary by university and country.",
            "prompt": "Prompt Engineering & Generative AI is an emerging skill/specialization pathway covering prompt design, LLM basics, RAG, evaluation and AI workflows. It is not a universally offered standalone B.Tech branch.",
        },
        "Telugu": {
            "title": "🤖 FuturePath AI సహాయకుడు",
            "welcome": "హాయ్! 👋 మీ విద్య మరియు కెరీర్ మార్గం గురించి నేను ఎలా సహాయం చేయగలను?",
            "placeholder": "మీ ప్రశ్నను టైప్ చేయండి...",
            "send": "పంపండి",
            "clear": "సంభాషణను క్లియర్ చేయండి",
            "typing": "FuturePath AI",
            "suggest": "✨ ఇవి అడగండి",
            "empty": "ముందుగా ఒక ప్రశ్న టైప్ చేయండి.",
            "fallback": "10వ తరగతి తర్వాత మార్గాలు, ఇంటర్మీడియట్ స్ట్రీమ్స్, ఇంజినీరింగ్ బ్రాంచులు, డిప్లొమా, ITI/వొకేషనల్, స్కిల్స్, ప్రాజెక్ట్స్, ఇంటర్న్‌షిప్స్, కెరీర్స్ మరియు M.Tech/MS గురించి నేను సహాయం చేయగలను.",
            "greeting": "హాయ్! 👋 నేను FuturePath AI. మీకు ఎలా సహాయం చేయగలను?",
            "mpc": "MPC తర్వాత B.Tech/B.E., B.Sc మరియు ఇతర సైన్స్/టెక్నాలజీ మార్గాలను ఎంచుకోవచ్చు. ఇంజినీరింగ్‌లో CSE, CSD, CSM, AI & ML, Data Science, Cyber Security, IT, ECE, EEE వంటి బ్రాంచులు ఉన్నాయి.",
            "intern": "ఇంటర్న్‌షిప్ కోసం సంబంధిత స్కిల్స్ నేర్చుకుని, 2–3 ప్రాజెక్టులు చేసి, GitHub/పోర్ట్‌ఫోలియో మరియు సింపుల్ రెజ్యూమ్ సిద్ధం చేసుకోండి.",
            "project": "Projects పేజీలో Beginner, Intermediate మరియు Advanced ప్రాజెక్ట్ ఐడియాలను చూడండి. ప్రతి ఇంజినీరింగ్ బ్రాంచ్‌లో కూడా సంబంధిత ప్రాజెక్టులు ఉన్నాయి.",
            "skill": "Skills పేజీలో Programming, Data Analytics, AI/ML, Technology, Engineering మరియు Soft Skills చూడవచ్చు.",
            "career": "Careers పేజీలో కెరీర్ రోల్స్ వెతికి, వాటికి సంబంధించిన బ్రాంచ్ మరియు మార్గాన్ని చూడండి.",
            "diploma": "Polytechnic / Diploma పేజీలో డిప్లొమా కోర్సులు, Subjects, Skills, Careers మరియు Further Study చూడండి.",
            "mtech": "ఒక Engineering Branch తెరిచి M.Tech ట్యాబ్‌లో B.Tech తర్వాత సాధారణ M.Tech మార్గాలను చూడండి.",
            "ms": "ఒక Engineering Branch తెరిచి MS ట్యాబ్‌లో B.Tech తర్వాత సాధారణ MS మార్గాలను చూడండి. కోర్సులు యూనివర్సిటీ మరియు దేశాన్ని బట్టి మారవచ్చు.",
            "prompt": "Prompt Engineering & Generative AI ఒక emerging skill/specialization pathway. ఇందులో Prompt Design, LLM basics, RAG, Evaluation మరియు AI workflows ఉంటాయి. ఇది ప్రతి కాలేజీలో standalone B.Tech branch కాదు.",
        },
        "Hindi": {
            "title": "🤖 FuturePath AI सहायक",
            "welcome": "नमस्ते! 👋 आपकी शिक्षा और करियर यात्रा में मैं कैसे मदद कर सकता हूँ?",
            "placeholder": "अपना सवाल लिखें...",
            "send": "भेजें",
            "clear": "बातचीत साफ करें",
            "typing": "FuturePath AI",
            "suggest": "✨ यह पूछें",
            "empty": "कृपया पहले अपना सवाल लिखें।",
            "fallback": "मैं कक्षा 10 के बाद के रास्तों, इंटरमीडिएट स्ट्रीम, इंजीनियरिंग शाखाओं, डिप्लोमा, ITI/वोकेशनल, स्किल्स, प्रोजेक्ट्स, इंटर्नशिप, करियर और M.Tech/MS में मदद कर सकता हूँ।",
            "greeting": "नमस्ते! 👋 मैं FuturePath AI हूँ। मैं आपकी कैसे मदद करूँ?",
            "mpc": "MPC के बाद B.Tech/B.E., B.Sc और अन्य विज्ञान/तकनीक विकल्प देख सकते हैं। इंजीनियरिंग में CSE, CSD, CSM, AI & ML, Data Science, Cyber Security, IT, ECE और EEE जैसी शाखाएँ हैं।",
            "intern": "इंटर्नशिप के लिए संबंधित स्किल्स सीखें, 2–3 प्रोजेक्ट बनाएं, GitHub/पोर्टफोलियो रखें और एक सरल रिज्यूमे तैयार करें।",
            "project": "Projects पेज पर Beginner, Intermediate और Advanced प्रोजेक्ट आइडिया देखें। शाखा के अनुसार प्रोजेक्ट भी देख सकते हैं।",
            "skill": "Skills पेज पर Programming, Data Analytics, AI/ML, Technology, Engineering और Soft Skills देखें।",
            "career": "Careers पेज पर करियर रोल खोजें और उससे जुड़ी शाखा और रोडमैप देखें।",
            "diploma": "Polytechnic / Diploma पेज पर डिप्लोमा कोर्स, विषय, स्किल्स, करियर और आगे की पढ़ाई देखें।",
            "mtech": "Engineering Branch खोलकर M.Tech टैब में B.Tech के बाद के संबंधित M.Tech विकल्प देखें।",
            "ms": "Engineering Branch खोलकर MS टैब में B.Tech के बाद के संबंधित MS विकल्प देखें। प्रोग्राम विश्वविद्यालय और देश के अनुसार बदल सकते हैं।",
            "prompt": "Prompt Engineering & Generative AI एक उभरता हुआ skill/specialization pathway है। इसमें Prompt Design, LLM basics, RAG, Evaluation और AI workflows शामिल हैं। यह हर कॉलेज में standalone B.Tech branch नहीं है।",
        },
        "Tamil": {
            "title": "🤖 FuturePath AI உதவியாளர்",
            "welcome": "வணக்கம்! 👋 உங்கள் கல்வி மற்றும் தொழில் பாதையில் நான் எப்படி உதவலாம்?",
            "placeholder": "உங்கள் கேள்வியை எழுதுங்கள்...",
            "send": "அனுப்பு",
            "clear": "உரையாடலை அழி",
            "typing": "FuturePath AI",
            "suggest": "✨ இதை கேளுங்கள்",
            "empty": "முதலில் ஒரு கேள்வியை எழுதுங்கள்.",
            "fallback": "10ஆம் வகுப்புக்குப் பிறகு கல்விப் பாதைகள், இடைநிலைப் பிரிவுகள், பொறியியல் கிளைகள், டிப்ளமா, ITI/தொழிற்பயிற்சி, திறன்கள், திட்டங்கள், இன்டர்ன்ஷிப், வேலைவாய்ப்புகள் மற்றும் M.Tech/MS பற்றி உதவ முடியும்.",
            "greeting": "வணக்கம்! 👋 நான் FuturePath AI. எப்படி உதவலாம்?",
            "mpc": "MPCக்குப் பிறகு B.Tech/B.E., B.Sc மற்றும் பிற அறிவியல்/தொழில்நுட்பப் பாதைகளைத் தேர்வு செய்யலாம். CSE, CSD, CSM, AI & ML, Data Science, Cyber Security, IT, ECE, EEE போன்ற பொறியியல் கிளைகள் உள்ளன.",
            "intern": "இன்டர்ன்ஷிப்புக்கு தொடர்புடைய திறன்களை கற்று, 2–3 திட்டங்களை உருவாக்கி, GitHub/portfolio மற்றும் எளிய resume தயாரிக்கவும்.",
            "project": "Projects பகுதியில் Beginner, Intermediate மற்றும் Advanced திட்டங்களைப் பார்க்கலாம்.",
            "skill": "Skills பகுதியில் Programming, Data Analytics, AI/ML, Technology, Engineering மற்றும் Soft Skills பார்க்கலாம்.",
            "career": "Careers பகுதியில் வேலைப் பாதைகளைத் தேடி, தொடர்புடைய branch-ஐப் பார்க்கலாம்.",
            "diploma": "Polytechnic / Diploma பகுதியில் பாடங்கள், திறன்கள், வேலைகள் மற்றும் மேல்படிப்பை பார்க்கலாம்.",
            "mtech": "Engineering Branch-ஐத் திறந்து M.Tech tab-ல் B.Techக்குப் பிறகு உள்ள தொடர்புடைய M.Tech பாதைகளைப் பார்க்கவும்.",
            "ms": "Engineering Branch-ஐத் திறந்து MS tab-ல் B.Techக்குப் பிறகு உள்ள தொடர்புடைய MS பாதைகளைப் பார்க்கவும்.",
            "prompt": "Prompt Engineering & Generative AI ஒரு வளர்ந்து வரும் skill/specialization pathway. இதில் Prompt Design, LLM basics, RAG மற்றும் AI workflows அடங்கும்.",
        },
        "Kannada": {
            "title": "🤖 FuturePath AI ಸಹಾಯಕ",
            "welcome": "ನಮಸ್ಕಾರ! 👋 ನಿಮ್ಮ ಶಿಕ್ಷಣ ಮತ್ತು ವೃತ್ತಿ ಮಾರ್ಗದಲ್ಲಿ ನಾನು ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
            "placeholder": "ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಟೈಪ್ ಮಾಡಿ...",
            "send": "ಕಳುಹಿಸಿ",
            "clear": "ಸಂಭಾಷಣೆಯನ್ನು ತೆರವುಗೊಳಿಸಿ",
            "typing": "FuturePath AI",
            "suggest": "✨ ಇದನ್ನು ಕೇಳಿ",
            "empty": "ಮೊದಲು ಪ್ರಶ್ನೆಯನ್ನು ಟೈಪ್ ಮಾಡಿ.",
            "fallback": "10ನೇ ತರಗತಿಯ ನಂತರದ ಮಾರ್ಗಗಳು, ಇಂಟರ್ಮೀಡಿಯೇಟ್ ಸ್ಟ್ರೀಮ್‌ಗಳು, ಎಂಜಿನಿಯರಿಂಗ್ ಶಾಖೆಗಳು, ಡಿಪ್ಲೊಮಾ, ITI/ವೊಕೇಶನಲ್, ಕೌಶಲ್ಯಗಳು, ಪ್ರಾಜೆಕ್ಟ್‌ಗಳು, ಇಂಟರ್ನ್‌ಶಿಪ್, ವೃತ್ತಿಗಳು ಮತ್ತು M.Tech/MS ಬಗ್ಗೆ ಸಹಾಯ ಮಾಡಬಹುದು.",
            "greeting": "ನಮಸ್ಕಾರ! 👋 ನಾನು FuturePath AI. ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?",
            "mpc": "MPC ನಂತರ B.Tech/B.E., B.Sc ಮತ್ತು ಇತರ ವಿಜ್ಞಾನ/ತಂತ್ರಜ್ಞಾನ ಮಾರ್ಗಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಬಹುದು. CSE, CSD, CSM, AI & ML, Data Science, Cyber Security, IT, ECE ಮತ್ತು EEE ಮುಂತಾದ ಶಾಖೆಗಳಿವೆ.",
            "intern": "ಇಂಟರ್ನ್‌ಶಿಪ್‌ಗಾಗಿ ಸಂಬಂಧಿತ ಕೌಶಲ್ಯಗಳನ್ನು ಕಲಿತು, 2–3 ಪ್ರಾಜೆಕ್ಟ್‌ಗಳನ್ನು ಮಾಡಿ, GitHub/portfolio ಮತ್ತು ಸರಳ resume ಸಿದ್ಧಪಡಿಸಿ.",
            "project": "Projects ಪುಟದಲ್ಲಿ Beginner, Intermediate ಮತ್ತು Advanced ಪ್ರಾಜೆಕ್ಟ್‌ಗಳನ್ನು ನೋಡಿ.",
            "skill": "Skills ಪುಟದಲ್ಲಿ Programming, Data Analytics, AI/ML, Technology, Engineering ಮತ್ತು Soft Skills ನೋಡಿ.",
            "career": "Careers ಪುಟದಲ್ಲಿ career roles ಹುಡುಕಿ ಸಂಬಂಧಿತ branch ಮತ್ತು pathway ನೋಡಿ.",
            "diploma": "Polytechnic / Diploma ಪುಟದಲ್ಲಿ courses, subjects, skills, careers ಮತ್ತು further study ನೋಡಿ.",
            "mtech": "Engineering Branch ತೆರೆಯಿರಿ ಮತ್ತು M.Tech tab ನಲ್ಲಿ B.Tech ನಂತರದ M.Tech ಮಾರ್ಗಗಳನ್ನು ನೋಡಿ.",
            "ms": "Engineering Branch ತೆರೆಯಿರಿ ಮತ್ತು MS tab ನಲ್ಲಿ B.Tech ನಂತರದ MS ಮಾರ್ಗಗಳನ್ನು ನೋಡಿ.",
            "prompt": "Prompt Engineering & Generative AI ಒಂದು emerging skill/specialization pathway. ಇದರಲ್ಲಿ Prompt Design, LLM basics, RAG ಮತ್ತು AI workflows ಇವೆ.",
        },
        "Malayalam": {
            "title": "🤖 FuturePath AI സഹായി",
            "welcome": "നമസ്കാരം! 👋 നിങ്ങളുടെ വിദ്യാഭ്യാസവും കരിയർ യാത്രയും സംബന്ധിച്ച് എങ്ങനെ സഹായിക്കാം?",
            "placeholder": "നിങ്ങളുടെ ചോദ്യം ടൈപ്പ് ചെയ്യൂ...",
            "send": "അയയ്ക്കുക",
            "clear": "സംഭാഷണം മായ്ക്കുക",
            "typing": "FuturePath AI",
            "suggest": "✨ ഇത് ചോദിക്കൂ",
            "empty": "ആദ്യം ഒരു ചോദ്യം ടൈപ്പ് ചെയ്യൂ.",
            "fallback": "10-ാം ക്ലാസിന് ശേഷമുള്ള വഴികൾ, ഇന്റർമീഡിയറ്റ് സ്ട്രീമുകൾ, എഞ്ചിനീയറിംഗ് ബ്രാഞ്ചുകൾ, ഡിപ്ലോമ, ITI/വൊക്കേഷണൽ, സ്കിൽസ്, പ്രോജക്റ്റുകൾ, ഇന്റേൺഷിപ്പുകൾ, കരിയർ, M.Tech/MS എന്നിവയിൽ സഹായിക്കാം.",
            "greeting": "നമസ്കാരം! 👋 ഞാൻ FuturePath AI ആണ്. എങ്ങനെ സഹായിക്കാം?",
            "mpc": "MPCയ്ക്ക് ശേഷം B.Tech/B.E., B.Sc എന്നിവയും മറ്റു സയൻസ്/ടെക്നോളജി വഴികളും തിരഞ്ഞെടുക്കാം. CSE, CSD, CSM, AI & ML, Data Science, Cyber Security, IT, ECE, EEE തുടങ്ങിയ ബ്രാഞ്ചുകൾ ഉണ്ട്.",
            "intern": "ഇന്റേൺഷിപ്പിനായി ബന്ധപ്പെട്ട സ്കിൽസ് പഠിക്കുക, 2–3 പ്രോജക്റ്റുകൾ നിർമ്മിക്കുക, GitHub/portfolioയും ലളിതമായ resumeയും തയ്യാറാക്കുക.",
            "project": "Projects പേജിൽ Beginner, Intermediate, Advanced പ്രോജക്റ്റുകൾ കാണാം.",
            "skill": "Skills പേജിൽ Programming, Data Analytics, AI/ML, Technology, Engineering, Soft Skills എന്നിവ കാണാം.",
            "career": "Careers പേജിൽ career roles തിരഞ്ഞ് ബന്ധപ്പെട്ട branch കാണാം.",
            "diploma": "Polytechnic / Diploma പേജിൽ courses, subjects, skills, careers, further study എന്നിവ കാണാം.",
            "mtech": "Engineering Branch തുറന്ന് M.Tech tab-ൽ B.Tech കഴിഞ്ഞുള്ള ബന്ധപ്പെട്ട M.Tech വഴികൾ കാണാം.",
            "ms": "Engineering Branch തുറന്ന് MS tab-ൽ B.Tech കഴിഞ്ഞുള്ള ബന്ധപ്പെട്ട MS വഴികൾ കാണാം.",
            "prompt": "Prompt Engineering & Generative AI ഒരു emerging skill/specialization pathway ആണ്. Prompt Design, LLM basics, RAG, Evaluation, AI workflows എന്നിവ ഉൾപ്പെടുന്നു.",
        },
        "Marathi": {
            "title": "🤖 FuturePath AI सहाय्यक",
            "welcome": "नमस्कार! 👋 तुमच्या शिक्षण आणि करिअरच्या मार्गात मी कशी मदत करू शकतो?",
            "placeholder": "तुमचा प्रश्न लिहा...",
            "send": "पाठवा",
            "clear": "संभाषण साफ करा",
            "typing": "FuturePath AI",
            "suggest": "✨ हे विचारून पाहा",
            "empty": "कृपया आधी प्रश्न लिहा.",
            "fallback": "इयत्ता 10 नंतरचे मार्ग, इंटरमिजिएट स्ट्रीम्स, इंजिनिअरिंग शाखा, डिप्लोमा, ITI/व्होकेशनल, स्किल्स, प्रोजेक्ट्स, इंटर्नशिप, करिअर आणि M.Tech/MS याबद्दल मदत करू शकतो.",
            "greeting": "नमस्कार! 👋 मी FuturePath AI आहे. मी तुम्हाला कशी मदत करू?",
            "mpc": "MPC नंतर B.Tech/B.E., B.Sc आणि इतर विज्ञान/तंत्रज्ञानाचे पर्याय पाहू शकता. CSE, CSD, CSM, AI & ML, Data Science, Cyber Security, IT, ECE, EEE अशा शाखा आहेत.",
            "intern": "इंटर्नशिपसाठी संबंधित skills शिका, 2–3 projects तयार करा, GitHub/portfolio आणि साधा resume तयार ठेवा.",
            "project": "Projects पेजवर Beginner, Intermediate आणि Advanced project ideas पाहा.",
            "skill": "Skills पेजवर Programming, Data Analytics, AI/ML, Technology, Engineering आणि Soft Skills पाहा.",
            "career": "Careers पेजवर career roles शोधा आणि संबंधित branch/pathway पाहा.",
            "diploma": "Polytechnic / Diploma पेजवर courses, subjects, skills, careers आणि पुढील शिक्षण पाहा.",
            "mtech": "Engineering Branch उघडून M.Tech tab मध्ये B.Tech नंतरचे संबंधित M.Tech मार्ग पाहा.",
            "ms": "Engineering Branch उघडून MS tab मध्ये B.Tech नंतरचे संबंधित MS मार्ग पाहा.",
            "prompt": "Prompt Engineering & Generative AI हा emerging skill/specialization pathway आहे. यात Prompt Design, LLM basics, RAG, Evaluation आणि AI workflows असतात.",
        },
        "Bengali": {
            "title": "🤖 FuturePath AI সহায়ক",
            "welcome": "নমস্কার! 👋 আপনার শিক্ষা ও ক্যারিয়ার পথে আমি কীভাবে সাহায্য করতে পারি?",
            "placeholder": "আপনার প্রশ্ন লিখুন...",
            "send": "পাঠান",
            "clear": "কথোপকথন পরিষ্কার করুন",
            "typing": "FuturePath AI",
            "suggest": "✨ এটি জিজ্ঞেস করুন",
            "empty": "অনুগ্রহ করে প্রথমে একটি প্রশ্ন লিখুন।",
            "fallback": "দশম শ্রেণির পরের পথ, ইন্টারমিডিয়েট স্ট্রিম, ইঞ্জিনিয়ারিং শাখা, ডিপ্লোমা, ITI/ভোকেশনাল, স্কিল, প্রজেক্ট, ইন্টার্নশিপ, ক্যারিয়ার এবং M.Tech/MS সম্পর্কে সাহায্য করতে পারি।",
            "greeting": "নমস্কার! 👋 আমি FuturePath AI। কীভাবে সাহায্য করতে পারি?",
            "mpc": "MPC-এর পরে B.Tech/B.E., B.Sc এবং অন্যান্য বিজ্ঞান/প্রযুক্তি পথ বেছে নিতে পারেন। CSE, CSD, CSM, AI & ML, Data Science, Cyber Security, IT, ECE, EEE ইত্যাদি শাখা রয়েছে।",
            "intern": "ইন্টার্নশিপের জন্য প্রাসঙ্গিক স্কিল শিখুন, 2–3টি প্রজেক্ট বানান, GitHub/portfolio এবং একটি সহজ resume প্রস্তুত করুন।",
            "project": "Projects পেজে Beginner, Intermediate এবং Advanced project ideas দেখুন।",
            "skill": "Skills পেজে Programming, Data Analytics, AI/ML, Technology, Engineering এবং Soft Skills দেখুন।",
            "career": "Careers পেজে career roles খুঁজে সম্পর্কিত branch ও pathway দেখুন।",
            "diploma": "Polytechnic / Diploma পেজে courses, subjects, skills, careers এবং further study দেখুন।",
            "mtech": "Engineering Branch খুলে M.Tech tab-এ B.Tech-এর পরের সম্পর্কিত M.Tech পথ দেখুন।",
            "ms": "Engineering Branch খুলে MS tab-এ B.Tech-এর পরের সম্পর্কিত MS পথ দেখুন।",
            "prompt": "Prompt Engineering & Generative AI একটি emerging skill/specialization pathway। এতে Prompt Design, LLM basics, RAG, Evaluation এবং AI workflows থাকে।",
        },
    }

    lang = st.session_state.get("language", "English")
    A = AI_LANG.get(lang, AI_LANG["English"])
    st.title(A["title"])
    st.caption("💬 " + A["typing"])

    if "ai_chat" not in st.session_state:
        st.session_state.ai_chat = [{"role": "assistant", "content": A["welcome"]}]
    elif st.session_state.get("ai_chat_language") != lang:
        # Keep the conversation, but start a localized greeting when the language changes.
        st.session_state.ai_chat = [{"role": "assistant", "content": A["welcome"]}]
    st.session_state.ai_chat_language = lang

    def conversational_answer(q):
        q_raw = q.strip()
        ql = q_raw.lower()
        if not ql:
            return A["empty"]
        greetings = ["hi", "hello", "hey", "hai", "namaste", "నమస్తే", "హాయ్", "నమస్కారం", "வணக்கம்", "नमस्ते", "ನಮಸ್ಕಾರ", "നമസ്കാരം", "नमस्कार", "নমস্কার"]
        if any(ql == g or ql.startswith(g + " ") for g in greetings):
            return A["greeting"]
        if "mpc" in ql or "m.p.c" in ql:
            return A["mpc"]
        if "intern" in ql or "ఇంటర్న్" in ql or "इंटर्न" in ql:
            return A["intern"]
        if "project" in ql or "ప్రాజెక్ట్" in ql or "प्रोजेक्ट" in ql:
            return A["project"]
        if "skill" in ql or "స్కిల్" in ql or "कौशल" in ql:
            return A["skill"]
        if "career" in ql or "కెరీర్" in ql or "करियर" in ql:
            return A["career"]
        if "diploma" in ql or "polytechnic" in ql or "డిప్లొమా" in ql or "डिप्लोमा" in ql:
            return A["diploma"]
        if "m.tech" in ql or "mtech" in ql or "ఎం.టెక్" in ql:
            return A["mtech"]
        if ql.startswith("ms") or " ms " in " " + ql + " " or "ఎంఎస్" in ql:
            return A["ms"]
        if "prompt" in ql or "generative ai" in ql or "జెనరేటివ్ ai" in ql:
            return A["prompt"]
        # Branch-aware responses from the existing FuturePath data.
        for name, d in BRANCHES.items():
            if name.lower() in ql:
                return (f"{name}: {d['description']} "
                        f"Key subjects: {', '.join(d['subjects'][:6])}. "
                        f"Career options: {', '.join(d['careers'][:5])}.")
        return A["fallback"]

    # Chat history
    for msg in st.session_state.ai_chat:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_msg = st.chat_input(A["placeholder"])
    if user_msg:
        st.session_state.ai_chat.append({"role": "user", "content": user_msg})
        answer = conversational_answer(user_msg)
        st.session_state.ai_chat.append({"role": "assistant", "content": answer})
        st.rerun()

    st.markdown("### " + A["suggest"])
    suggestions = {
        "English": ["Hi", "What can I do after MPC?", "What are M.Tech options after CSE?", "How can I prepare for an internship?"],
        "Telugu": ["హాయ్", "MPC తర్వాత ఏమి చేయవచ్చు?", "CSE తర్వాత M.Tech options ఏమిటి?", "ఇంటర్న్‌షిప్ కోసం ఎలా సిద్ధం కావాలి?"],
        "Hindi": ["नमस्ते", "MPC के बाद क्या कर सकते हैं?", "CSE के बाद M.Tech options क्या हैं?", "इंटर्नशिप के लिए कैसे तैयारी करें?"],
        "Tamil": ["வணக்கம்", "MPCக்குப் பிறகு என்ன செய்யலாம்?", "CSEக்கு பிறகு M.Tech options என்ன?", "இன்டர்ன்ஷிப்புக்கு எப்படி தயாராகலாம்?"],
        "Kannada": ["ನಮಸ್ಕಾರ", "MPC ನಂತರ ಏನು ಮಾಡಬಹುದು?", "CSE ನಂತರ M.Tech options ಏನು?", "ಇಂಟರ್ನ್‌ಶಿಪ್‌ಗೆ ಹೇಗೆ ಸಿದ್ಧರಾಗಬೇಕು?"],
        "Malayalam": ["നമസ്കാരം", "MPC കഴിഞ്ഞ് എന്ത് ചെയ്യാം?", "CSE കഴിഞ്ഞുള്ള M.Tech options എന്തൊക്കെയാണ്?", "ഇന്റേൺഷിപ്പിന് എങ്ങനെ തയ്യാറാകാം?"],
        "Marathi": ["नमस्कार", "MPC नंतर काय करू शकतो?", "CSE नंतर M.Tech options कोणते?", "इंटर्नशिपसाठी कशी तयारी करावी?"],
        "Bengali": ["নমস্কার", "MPC-এর পরে কী করা যায়?", "CSE-এর পরে M.Tech options কী?", "ইন্টার্নশিপের জন্য কীভাবে প্রস্তুতি নেব?"],
    }
    cols = st.columns(2)
    for i, suggestion in enumerate(suggestions.get(lang, suggestions["English"])):
        with cols[i % 2]:
            if st.button("💡 " + suggestion, key="ai_suggestion_" + str(i), use_container_width=True):
                st.session_state.ai_chat.append({"role": "user", "content": suggestion})
                st.session_state.ai_chat.append({"role": "assistant", "content": conversational_answer(suggestion)})
                st.rerun()

    if st.button("🗑️ " + A["clear"], use_container_width=True):
        st.session_state.ai_chat = [{"role": "assistant", "content": A["welcome"]}]
        st.rerun()

elif st.session_state.page=="quiz":
    st.title("🎯 "+T["quiz"]+"")
    q1=st.radio("1. What do you enjoy?",["Coding / Computers","Data / Numbers","Electronics","Machines / Construction","Biology / Agriculture","AI / Robots"])
    q2=st.radio("2. Which project sounds interesting?",["Build an app","Analyze student data","Build an electronic device","Design a machine/building","Study plants/biology","Build an AI/robot"])
    if st.button("🔍 Show suggested area",use_container_width=True):
        s=q1+q2
        if "Data" in s or "student data" in s: r="📊 Data & Analytics"
        elif "Coding" in s or "app" in s: r="💻 Computer & Technology"
        elif "Electronics" in s or "electronic" in s: r="📡 Electronics & Electrical"
        elif "Machines" in s or "machine/building" in s: r="⚙️ Core Engineering"
        elif "Biology" in s or "plants" in s: r="🌱 Agriculture & Life Sciences"
        else: r="🤖 AI / Robotics"
        st.success("Suggested area: "+r)
        st.info("Use this only as an exploration aid; compare multiple branches, subjects, costs, eligibility and your interests before deciding.")

st.markdown("---")
st.markdown('<div class="footer">🌈 <b>FuturePath</b><br>Your Career. Your Future. Your Path. 🚀<br><br>Explore • Learn • Build • Intern • Grow</div>',unsafe_allow_html=True)
