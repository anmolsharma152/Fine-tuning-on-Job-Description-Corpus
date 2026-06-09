#!/usr/bin/env python3
"""
scraper.py
Provides web scraping scaffolding and a high-fidelity synthetic generator
for India-focused job descriptions.
"""
import os
import json
import random
import argparse
from typing import List, Dict, Any
import urllib.request
from bs4 import BeautifulSoup

# Define components for synthetic generation
CITIES = ["Bengaluru", "Noida", "Gurugram", "Mumbai", "Hyderabad", "Pune", "Chennai"]
COMPANIES = [
    "TCS", "Infosys", "Wipro", "Google India", "Swiggy", "Zomato",
    "Reliance Jio", "Paytm", "Cred", "Flipkart", "Tech Mahindra", "HCLTech"
]

ROLE_TEMPLATES = {
    "Software Engineering": {
        "titles": ["Frontend Developer", "Backend Engineer", "Full Stack Developer", "DevOps Engineer", "QA Automation Engineer"],
        "skills": ["Python", "JavaScript", "React", "Node.js", "Java", "Spring Boot", "AWS", "Docker", "Kubernetes", "SQL", "Git", "Go"],
        "responsibilities": [
            "Design, develop, and maintain clean, scalable, and efficient web services and applications.",
            "Collaborate with product managers and UX designers to build intuitive user interfaces.",
            "Build and optimize CI/CD pipelines to automate testing and deployments.",
            "Write comprehensive unit and integration tests to ensure system reliability.",
            "Participate in design discussions, code reviews, and agile sprints."
        ]
    },
    "Data Science": {
        "titles": ["Data Scientist", "Machine Learning Engineer", "Data Analyst", "NLP Research Engineer", "Data Engineer"],
        "skills": ["Python", "SQL", "PyTorch", "TensorFlow", "Pandas", "Scikit-Learn", "Hugging Face", "Apache Spark", "Tableau", "PowerBI"],
        "responsibilities": [
            "Develop, train, and evaluate machine learning models for production applications.",
            "Clean, analyze, and interpret large, complex datasets to extract actionable business insights.",
            "Build robust data pipelines to ingest, transform, and store data at scale.",
            "Design and execute A/B tests to validate model performance and user behavior.",
            "Communicate complex technical findings to non-technical stakeholders."
        ]
    },
    "Product Management": {
        "titles": ["Product Manager", "Associate Product Manager", "Technical Product Manager", "Product Lead"],
        "skills": ["Product Strategy", "Agile Methodologies", "Jira", "SQL", "A/B Testing", "User Research", "Wireframing", "Roadmapping"],
        "responsibilities": [
            "Define the product vision, roadmap, and requirements for new feature releases.",
            "Conduct market and user research to identify customer pain points and opportunities.",
            "Work closely with engineering and design teams to guide product development cycles.",
            "Define and analyze key performance indicators (KPIs) to measure product success.",
            "Align cross-functional stakeholders on project timelines and product launch strategies."
        ]
    },
    "Marketing": {
        "titles": ["Digital Marketing Specialist", "SEO Analyst", "Content Marketer", "Growth Marketing Manager", "Social Media Lead"],
        "skills": ["SEO", "Google Analytics", "Content Writing", "Copywriting", "Email Marketing", "Social Media Ads", "A/B Testing"],
        "responsibilities": [
            "Plan and execute end-to-end digital marketing campaigns across SEO, SEM, and social channels.",
            "Create high-quality written and visual content to drive organic traffic and lead generation.",
            "Analyze campaign performance and website traffic metrics to optimize ROI.",
            "Manage paid ad spend on Google, Meta, and LinkedIn to acquire new users.",
            "Collaborate with creative teams to design landing pages, newsletters, and ad creatives."
        ]
    },
    "HR": {
        "titles": ["HR Recruiter", "HR Generalist", "Talent Acquisition Partner", "HR Manager", "Compensation Analyst"],
        "skills": ["Talent Acquisition", "Employee Relations", "Onboarding", "Payroll Management", "Applicant Tracking Systems", "Interviewing"],
        "responsibilities": [
            "Manage the end-to-end recruitment lifecycle, from sourcing to onboarding candidates.",
            "Develop and implement HR policies, employee engagement initiatives, and retention strategies.",
            "Address employee grievances and foster a collaborative, positive workplace culture.",
            "Administer payroll processes, benefits programs, and performance review cycles.",
            "Partner with department heads to forecast hiring needs and build talent pipelines."
        ]
    },
    "Finance": {
        "titles": ["Financial Analyst", "Accountant", "Investment Analyst", "Finance Manager", "Risk Manager"],
        "skills": ["Excel", "Tally ERP", "Financial Modeling", "Corporate Finance", "Taxation", "Auditing", "Risk Analysis"],
        "responsibilities": [
            "Prepare monthly, quarterly, and annual financial statements and reports.",
            "Perform budget forecasting, cost-benefit analysis, and financial variance tracking.",
            "Ensure compliance with local taxation laws, corporate policies, and accounting standards.",
            "Conduct financial modeling to support business decisions, partnerships, and investments.",
            "Identify financial risks and implement controls to mitigate them."
        ]
    }
}

EXPERIENCE_LEVELS = [
    {"level": "0-2 years", "bucket": "Entry"},
    {"level": "3-5 years", "bucket": "Mid"},
    {"level": "5-8 years", "bucket": "Senior"},
    {"level": "8+ years", "bucket": "Executive"}
]

SALARY_MULTIPLIERS = {
    "Entry": (300000, 800000),
    "Mid": (800000, 1800000),
    "Senior": (1800000, 3500000),
    "Executive": (3500000, 7000000)
}

ROLE_MULTIPLIERS = {
    "Software Engineering": 1.2,
    "Data Science": 1.25,
    "Product Management": 1.15,
    "Marketing": 0.85,
    "HR": 0.8,
    "Finance": 0.95
}

def format_salary(val: int) -> str:
    """Format integer salary to INR currency string format."""
    return f"INR {val:,}"

def generate_synthetic_job(job_id: int) -> Dict[str, Any]:
    """Generate a single high-fidelity India-focused job description record with multilingual variations."""
    category = random.choice(list(ROLE_TEMPLATES.keys()))
    role_info = ROLE_TEMPLATES[category]
    
    title = random.choice(role_info["titles"])
    company = random.choice(COMPANIES)
    location = random.choice(CITIES)
    exp_info = random.choice(EXPERIENCE_LEVELS)
    
    # Select subset of skills
    num_skills = random.randint(3, 6)
    skills_list = random.sample(role_info["skills"], min(num_skills, len(role_info["skills"])))
    skills_str = ", ".join(skills_list)
    
    # Calculate salary range based on category, experience, and noise
    base_min, base_max = SALARY_MULTIPLIERS[exp_info["bucket"]]
    multiplier = ROLE_MULTIPLIERS[category]
    
    min_sal = int(base_min * multiplier * random.uniform(0.9, 1.1))
    max_sal = int(base_max * multiplier * random.uniform(0.9, 1.1))
    
    # Round to nearest 50,000 INR
    min_sal = (min_sal // 50000) * 50000
    max_sal = (max_sal // 50000) * 50000
    
    salary_str = f"₹{min_sal:,} - ₹{max_sal:,} per annum"
    
    # Select language mix (40% English, 20% Hindi, 20% Hinglish, 20% Broken English)
    lang = random.choices(
        ["English", "Hindi", "Hinglish", "Broken_English"],
        weights=[40, 20, 20, 20],
        k=1
    )[0]
    
    responsibilities = random.sample(role_info["responsibilities"], 3)
    
    if lang == "English":
        resp_bullets = "\n".join([f"- {resp}" for resp in responsibilities])
        company_intro = (
            f"At {company}, we are shaping the future of our industry in India and beyond. "
            f"Our team in {location} is expanding rapidly, and we are looking for top talent to join us "
            f"on our mission to build world-class products and solutions."
        )
        job_desc = (
            f"**Company Overview:**\n{company_intro}\n\n"
            f"**Role Summary:**\nWe are looking for a dedicated and energetic {title} with {exp_info['level']} "
            f"of experience. In this role, you will be part of our dynamic team in {location}, playing a key "
            f"part in the development and optimization of our operations.\n\n"
            f"**Key Responsibilities:**\n{resp_bullets}\n\n"
            f"**Requirements:**\n"
            f"- {exp_info['level']} of relevant experience in a similar function.\n"
            f"- Strong proficiency in: {skills_str}.\n"
            f"- Solid understanding of industry best practices and standards.\n"
            f"- Excellent communication, teamwork, and problem-solving skills.\n\n"
            f"**Compensation & Benefits:**\n"
            f"- Annual Salary: {salary_str}\n"
            f"- Comprehensive medical coverage for employee and dependents.\n"
            f"- Continuous learning allowance and professional certifications support.\n"
            f"- Hybrid work setup with flexible timings."
        )
    elif lang == "Hindi":
        # Hindi translations of key responsibilities
        hindi_resps = {
            "Design, develop, and maintain clean, scalable, and efficient web services and applications.": "क्लीन, स्केलेबल और कुशल वेब सेवाओं और अनुप्रयोगों का डिज़ाइन, विकास और रखरखाव करना।",
            "Collaborate with product managers and UX designers to build intuitive user interfaces.": "सहज उपयोगकर्ता इंटरफ़ेस बनाने के लिए उत्पाद प्रबंधकों और यूएक्स डिजाइनरों के साथ सहयोग करना।",
            "Build and optimize CI/CD pipelines to automate testing and deployments.": "परीक्षण और तैनाती को स्वचालित करने के लिए सीआई/सीडी पाइपलाइनों का निर्माण और अनुकूलन करना।",
            "Write comprehensive unit and integration tests to ensure system reliability.": "प्रणाली की विश्वसनीयता सुनिश्चित करने के लिए व्यापक इकाई और एकीकरण परीक्षण लिखना।",
            "Participate in design discussions, code reviews, and agile sprints.": "डिज़ाइन चर्चाओं, कोड समीक्षाओं और फुर्तीले (agile) स्प्रिंट में भाग लेना।",
            "Develop, train, and evaluate machine learning models for production applications.": "उत्पादन अनुप्रयोगों के लिए मशीन लर्निंग मॉडल का विकास, प्रशिक्षण और मूल्यांकन करना।",
            "Clean, analyze, and interpret large, complex datasets to extract actionable business insights.": "व्यावहारिक व्यावसायिक अंतर्दृष्टि प्राप्त करने के लिए बड़े और जटिल डेटासेट को साफ़, विश्लेषण और व्याख्या करना।",
            "Build robust data pipelines to ingest, transform, and store data at scale.": "पैमाने पर डेटा प्राप्त करने, परिवर्तित करने और संग्रहीत करने के लिए मजबूत डेटा पाइपलाइनों का निर्माण करना।",
            "Design and execute A/B tests to validate model performance and user behavior.": "मॉडल प्रदर्शन और उपयोगकर्ता व्यवहार को सत्यापित करने के लिए ए/बी परीक्षणों का डिज़ाइन और निष्पादन करना।",
            "Communicate complex technical findings to non-technical stakeholders.": "गैर-तकनीकी हितधारकों को जटिल तकनीकी निष्कर्षों के बारे में समझाना।",
            "Define the product vision, roadmap, and requirements for new feature releases.": "नए फीचर रिलीज़ के लिए उत्पाद दृष्टिकोण, रोडमैप और आवश्यकताओं को परिभाषित करना।",
            "Conduct market and user research to identify customer pain points and opportunities.": "ग्राहक की समस्याओं और अवसरों की पहचान करने के लिए बाजार और उपयोगकर्ता अनुसंधान करना।",
            "Work closely with engineering and design teams to guide product development cycles.": "उत्पाद विकास चक्रों का मार्गदर्शन करने के लिए इंजीनियरिंग और डिज़ाइन टीमों के साथ मिलकर काम करना।",
            "Define and analyze key performance indicators (KPIs) to measure product success.": "उत्पाद की सफलता को मापने के लिए प्रमुख प्रदर्शन संकेतकों (KPI) को परिभाषित और विश्लेषण करना।",
            "Align cross-functional stakeholders on project timelines and product launch strategies.": "परियोजना समयसीमा और उत्पाद लॉन्च रणनीतियों पर क्रॉस-फंक्शनल हितधारकों को संरेखित करना।",
            "Plan and execute end-to-end digital marketing campaigns across SEO, SEM, and social channels.": "एसईओ, एसईएम और सोशल चैनलों पर शुरू से अंत तक डिजिटल मार्केटिंग अभियान योजना बनाना और निष्पादित करना।",
            "Create high-quality written and visual content to drive organic traffic and lead generation.": "ऑर्गेनिक ट्रैफ़िक और लीड जनरेशन बढ़ाने के लिए उच्च गुणवत्ता वाली लिखित और दृश्य सामग्री बनाना।",
            "Analyze campaign performance and website traffic metrics to optimize ROI.": "आरओआई को अनुकूलित करने के लिए अभियान प्रदर्शन और वेबसाइट ट्रैफ़िक मेट्रिक्स का विश्लेषण करना।",
            "Manage paid ad spend on Google, Meta, and LinkedIn to acquire new users.": "नए उपयोगकर्ताओं को प्राप्त करने के लिए Google, Meta और LinkedIn पर सशुल्क विज्ञापन खर्च प्रबंधित करना।",
            "Collaborate with creative teams to design landing pages, newsletters, and ad creatives.": "लैंडिंग पेज, न्यूज़लेटर्स और विज्ञापन क्रिएटिव डिज़ाइन करने के लिए रचनात्मक टीमों के साथ सहयोग करना।",
            "Manage the end-to-end recruitment lifecycle, from sourcing to onboarding candidates.": "उम्मीदवारों की खोज से लेकर ऑनबोर्डिंग तक भर्ती चक्र का प्रबंधन करना।",
            "Develop and implement HR policies, employee engagement initiatives, and retention strategies.": "एचआर नीतियों, कर्मचारी जुड़ाव पहलों और प्रतिधारण रणनीतियों का विकास और कार्यान्वयन करना।",
            "Address employee grievances and foster a collaborative, positive workplace culture.": "कर्मचारियों की शिकायतों का समाधान करना और एक सहयोगी, सकारात्मक कार्यस्थल संस्कृति को बढ़ावा देना।",
            "Administer payroll processes, benefits programs, and performance review cycles.": "पेरोल प्रक्रियाओं, लाभ कार्यक्रमों और प्रदर्शन समीक्षा चक्रों का संचालन करना।",
            "Partner with department heads to forecast hiring needs and build talent pipelines.": "भर्ती आवश्यकताओं का पूर्वानुमान लगाने और प्रतिभा पाइपलाइनों के निर्माण के लिए विभाग प्रमुखों के साथ साझेदारी करना।",
            "Prepare monthly, quarterly, and annual financial statements and reports.": "मासिक, त्रैमासिक और वार्षिक वित्तीय विवरण और रिपोर्ट तैयार करना।",
            "Perform budget forecasting, cost-benefit analysis, and financial variance tracking.": "बजट पूर्वानुमान, लागत-लाभ विश्लेषण और वित्तीय भिन्नता ट्रैकिंग निष्पादित करना।",
            "Ensure compliance with local taxation laws, corporate policies, and standards.": "स्थानीय कराधान कानूनों, कॉर्पोरेट नीतियों और मानकों का अनुपालन सुनिश्चित करना।",
            "Conduct financial modeling to support business decisions, partnerships, and investments.": "व्यावसायिक निर्णयों, साझेदारियों और निवेशों का समर्थन करने के लिए वित्तीय मॉडलिंग करना।",
            "Identify financial risks and implement controls to mitigate them.": "वित्तीय जोखिमों की पहचान करना और उन्हें कम करने के लिए नियंत्रण लागू करना।"
        }
        
        resp_hindi_list = []
        for resp in responsibilities:
            resp_hindi_list.append(hindi_resps.get(resp, "भूमिका के अनुसार दैनिक कार्य सौंपे गए कर्तव्यों को पूरा करना।"))
            
        resp_bullets = "\n".join([f"- {resp}" for resp in resp_hindi_list])
        
        company_intro = (
            f"{company} में, हम भारत और उसके बाहर अपने उद्योग के भविष्य को आकार दे रहे हैं। "
            f"{location} में हमारी टीम तेजी से बढ़ रही है, और हम अपने विश्व स्तरीय उत्पादों और "
            f"समाधानों को बनाने के मिशन में शामिल होने के लिए बेहतरीन प्रतिभाओं की तलाश कर रहे हैं।"
        )
        
        job_desc = (
            f"**कंपनी विवरण:**\n{company_intro}\n\n"
            f"**भूमिका सारांश:**\nहम {location} में हमारी गतिशील टीम के लिए {exp_info['level']} "
            f"के अनुभव के साथ एक समर्पित और ऊर्जावान {title} की तलाश कर रहे हैं। इस भूमिका में, "
            f"आप हमारे कार्यों के विकास और अनुकूलन में महत्वपूर्ण भूमिका निभाएंगे।\n\n"
            f"**मुख्य जिम्मेदारियां:**\n{resp_bullets}\n\n"
            f"**आवश्यकताएं:**\n"
            f"- समान कार्य में कम से कम {exp_info['level']} का अनुभव होना चाहिए।\n"
            f"- मुख्य कौशल (Skills): {skills_str}.\n"
            f"- उद्योग की सर्वोत्तम प्रथाओं और मानकों की अच्छी समझ।\n"
            f"- बेहतरीन संचार, टीमवर्क और समस्या समाधान कौशल।\n\n"
            f"**वेतन और लाभ:**\n"
            f"- वार्षिक वेतन (Salary): {salary_str}\n"
            f"- कर्मचारी और आश्रितों के लिए व्यापक चिकित्सा बीमा कवरेज।\n"
            f"- लचीला काम (Hybrid work setup) और काम के घंटे।"
        )
    elif lang == "Hinglish":
        # Hinglish translations
        hinglish_resps = {
            "Design, develop, and maintain clean, scalable, and efficient web services and applications.": "Scalable aur efficient web services aur apps ko design, develop aur maintain karna.",
            "Collaborate with product managers and UX designers to build intuitive user interfaces.": "Intuitive user interfaces banane ke liye product managers aur UX designers ke sath milkar kaam karna.",
            "Build and optimize CI/CD pipelines to automate testing and deployments.": "Testing aur deployments automate karne ke liye CI/CD pipelines build aur optimize karna.",
            "Write comprehensive unit and integration tests to ensure system reliability.": "System reliability ensure karne ke liye unit aur integration tests likhna.",
            "Participate in design discussions, code reviews, and agile sprints.": "Design discussions, code reviews aur agile sprints mein active participate karna.",
            "Develop, train, and evaluate machine learning models for production applications.": "Production applications ke liye machine learning models train, develop aur evaluate karna.",
            "Clean, analyze, and interpret large, complex datasets to extract actionable business insights.": "Business insights nikalne ke liye complex datasets ko clean aur analyze karna.",
            "Build robust data pipelines to ingest, transform, and store data at scale.": "Scale pe data ingest, transform aur store karne ke liye robust data pipelines banana.",
            "Design and execute A/B tests to validate model performance and user behavior.": "Model performance aur user behavior validate karne ke liye A/B tests chalana.",
            "Communicate complex technical findings to non-technical stakeholders.": "Non-technical stakeholders ke sath technical findings discuss aur explain karna.",
            "Define the product vision, roadmap, and requirements for new feature releases.": "New feature releases ke liye product vision, roadmap aur requirements taiyar karna.",
            "Conduct market and user research to identify customer pain points and opportunities.": "Customer requirements aur opportunities identify karne ke liye user research karna.",
            "Work closely with engineering and design teams to guide product development cycles.": "Product development cycles guide karne ke liye engineers aur designers ke sath closely kaam karna.",
            "Define and analyze key performance indicators (KPIs) to measure product success.": "Product success measure karne ke liye KPIs define aur analyze karna.",
            "Align cross-functional stakeholders on project timelines and product launch strategies.": "Project timelines aur launch strategies pe cross-functional teams ko align karna.",
            "Plan and execute end-to-end digital marketing campaigns across SEO, SEM, and social channels.": "SEO, SEM aur social channels pe end-to-end digital marketing campaigns plan aur run karna.",
            "Create high-quality written and visual content to drive organic traffic and lead generation.": "Organic traffic aur leads badhane ke liye high-quality content aur creatives ready karna.",
            "Analyze campaign performance and website traffic metrics to optimize ROI.": "ROI optimize karne ke liye campaign performance aur website traffic metrics analyze karna.",
            "Manage paid ad spend on Google, Meta, and LinkedIn to acquire new users.": "New users lane ke liye Google, Meta aur LinkedIn pe paid ad spend manage karna.",
            "Collaborate with creative teams to design landing pages, newsletters, and ad creatives.": "Landing pages, newsletters aur ad creatives ready karne ke liye creative teams ke sath kaam karna.",
            "Manage the end-to-end recruitment lifecycle, from sourcing to onboarding candidates.": "Sourcing se lekar onboarding tak recruitment lifecycle manage karna.",
            "Develop and implement HR policies, employee engagement initiatives, and retention strategies.": "HR policies aur employee engagement programs design aur implement karna.",
            "Address employee grievances and foster a collaborative, positive workplace culture.": "Employee complaints solve karna aur positive workplace culture maintain karna.",
            "Administer payroll processes, benefits programs, and performance review cycles.": "Payroll processes aur performance review cycles handle karna.",
            "Partner with department heads to forecast hiring needs and build talent pipelines.": "Hiring needs forecast karne ke liye department heads ke sath collaborate karna.",
            "Prepare monthly, quarterly, and annual financial statements and reports.": "Financial statements aur monthly/yearly reports ready karna.",
            "Perform budget forecasting, cost-benefit analysis, and financial variance tracking.": "Budget forecasting aur cost-benefit analysis prepare karna.",
            "Ensure compliance with local taxation laws, corporate policies, and standards.": "Taxation laws aur corporate policies ke sath compliance ensure karna.",
            "Conduct financial modeling to support business decisions, partnerships, and investments.": "Business decisions aur investments support karne ke liye financial modeling karna.",
            "Identify financial risks and implement controls to mitigate them.": "Financial risks identify karke unhe control karne ke methods implement karna."
        }
        resp_hinglish_list = []
        for resp in responsibilities:
            resp_hinglish_list.append(hinglish_resps.get(resp, "Role ke duties aur daily assignments handle karna."))
            
        resp_bullets = "\n".join([f"- {resp}" for resp in resp_hinglish_list])
        
        company_intro = (
            f"At {company}, hum industry ka future shape kar rahe hain India mein. "
            f"Humari {location} team bahut fast grow kar rahi hai, aur humein top talent ki zaroorat hai "
            f"jo humare sath milkar world-class products bana sakein."
        )
        
        job_desc = (
            f"**Company ke baare mein:**\n{company_intro}\n\n"
            f"**Role Summary:**\nHumein ek energetic {title} chahiye jiske paas {exp_info['level']} "
            f"ka experience ho. Aap humari {location} team ke sath kaam karenge aur operations ko grow "
            f"karne mein help karenge.\n\n"
            f"**Key Responsibilities:**\n{resp_bullets}\n\n"
            f"**Requirements:**\n"
            f"- Kam se kam {exp_info['level']} ka experience hona chahiye same field mein.\n"
            f"- In skills pe strong command honi chahiye: {skills_str}.\n"
            f"- Industry standards aur best practices ki knowledge.\n"
            f"- Achi communication aur teamwork skills.\n\n"
            f"**Salary aur Benefits:**\n"
            f"- Annual CTC: {salary_str}\n"
            f"- Health insurance for you and family.\n"
            f"- Hybrid work setup with flexible timings."
        )
    else:  # Broken English
        resp_broken_list = [
            f"Need to do {skills_list[0]} and {skills_list[1]} work daily.",
            "Must handle project updates and work with other developers.",
            "Fixing code bugs and checking client issues fast."
        ]
        resp_bullets = "\n".join([f"- {resp}" for resp in resp_broken_list])
        
        job_desc = (
            f"**About Company:**\nUrgent hiring in {company} company. We are growing very fast in {location} "
            f"location. Recruiting immediate joiner for {title} job.\n\n"
            f"**Job Work:**\nWork as {title} in our office located at {location}. "
            f"Must have {exp_info['level']} work knowledge.\n\n"
            f"**Responsibility:**\n{resp_bullets}\n\n"
            f"**Candidate Requirement:**\n"
            f"- Experience must be minimum {exp_info['level']}.\n"
            f"- Candidate must know skills: {skills_str}.\n"
            f"- Good communication not mandatory but work should be perfect.\n"
            f"- Immediate joiner preferred.\n\n"
            f"**Salary:**\n"
            f"- Salary will be {salary_str} (negotiable for good candidate)\n"
            f"- Monthly bonus extra and standard medical insurance."
        )
        
    return {
        "job_id": f"IND-{job_id:06d}",
        "job_title": title,
        "company": company,
        "location": location,
        "role_category": category,
        "experience_required": exp_info["level"],
        "salary_bucket": exp_info["bucket"],
        "min_salary_inr": min_sal,
        "max_salary_inr": max_sal,
        "skills": skills_list,
        "language": lang,
        "job_description": job_desc
    }

def scrape_jobs_from_public_repo(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Mock scraper that demonstrates how web scraping would run.
    As external websites have heavy Cloudflare protections, this script queries a public
    dataset or parses a mock local webpage.
    """
    print(f"Starting mock web scrape for up to {limit} jobs...")
    scraped_jobs = []
    
    # We can create a mock webpage internally to demonstrate parsing
    mock_html = """
    <html>
      <body>
        <div class="job-card" data-id="101">
          <h2 class="title">React Native Engineer</h2>
          <span class="company">Zomato India</span>
          <span class="location">Gurugram</span>
          <p class="description">Responsible for building cross-platform mobile apps using React Native. Requires 3+ years experience with JS/TS.</p>
          <span class="salary">₹1,500,000 - ₹2,500,000</span>
        </div>
        <div class="job-card" data-id="102">
          <h2 class="title">Lead Data Engineer</h2>
          <span class="company">Swiggy</span>
          <span class="location">Bengaluru</span>
          <p class="description">Looking for a Lead Data Engineer to design high-throughput stream pipelines using PySpark and Kafka. 6+ years experience.</p>
          <span class="salary">₹2,800,000 - ₹4,200,000</span>
        </div>
      </body>
    </html>
    """
    soup = BeautifulSoup(mock_html, 'html.parser')
    cards = soup.find_all('div', class_='job-card')
    
    for idx, card in enumerate(cards):
        title = card.find('h2', class_='title').text
        company = card.find('span', class_='company').text
        location = card.find('span', class_='location').text
        desc = card.find('p', class_='description').text
        sal = card.find('span', class_='salary').text
        
        scraped_jobs.append({
            "job_id": f"SCR-{idx:04d}",
            "job_title": title,
            "company": company,
            "location": location,
            "role_category": "Software Engineering" if "Engineer" in title else "Data Science",
            "experience_required": "3-5 years" if "React" in title else "5-8 years",
            "salary_bucket": "Mid" if "React" in title else "Senior",
            "min_salary_inr": 1500000 if "React" in title else 2800000,
            "max_salary_inr": 2500000 if "React" in title else 4200000,
            "skills": ["React Native", "JavaScript"] if "React" in title else ["PySpark", "Kafka"],
            "job_description": f"**Company Overview:**\nJoin our team at {company} in {location}.\n\n**Role Summary:**\n{desc}\n\n**Compensation:**\nSalary range: {sal}"
        })
        
    print(f"Mock scrape completed. Extracted {len(scraped_jobs)} jobs.")
    return scraped_jobs

def main():
    parser = argparse.ArgumentParser(description="Job description scraper and generator")
    parser.add_argument("--generate", action="store_true", help="Generate synthetic India-focused job corpus")
    parser.add_argument("--count", type=int, default=10000, help="Number of synthetic job descriptions to generate")
    parser.add_argument("--scrape", action="store_true", help="Run the mock scraping utility")
    parser.add_argument("--output", type=str, default="data/raw_jobs.jsonl", help="Output path for the generated dataset")
    
    args = parser.parse_args()
    
    # Ensure directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    all_jobs = []
    
    if args.scrape:
        scraped = scrape_jobs_from_public_repo()
        all_jobs.extend(scraped)
        
    if args.generate or not all_jobs:
        print(f"Generating {args.count} high-fidelity Indian job descriptions...")
        for i in range(args.count):
            all_jobs.append(generate_synthetic_job(i + 1))
            
    # Write to JSONL
    print(f"Saving {len(all_jobs)} jobs to {args.output}...")
    with open(args.output, "w", encoding="utf-8") as f:
        for job in all_jobs:
            f.write(json.dumps(job, ensure_ascii=False) + "\n")
            
    print("Data collection step completed successfully!")

if __name__ == "__main__":
    main()
