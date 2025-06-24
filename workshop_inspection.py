import streamlit as st
import pandas as pd
from PIL import Image
import io
import base64
from datetime import datetime
import json
import time
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Workshop Inspection Tool",
    page_icon="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAMAAABF0y+mAAAAeFBMVEVHcEz49fWgnp8jHyA/PD18eXojHyAfGxw2MzReW1wjHyAtKStHRUWlpKP0cXZBPz/vO0L38PD49/ftGiLtHCTvMjj4q68pJibtHCTtGCDxXWLwRkv3o6btFR7yZ2tOS0xRTk8TDQ+SkJFbWFlqaGljYGLvP0XtEBogSfLOAAAAJ3RSTlMACBk65lY2//CE//+1OVPYxxMky//sTPXJ/5CzLf+Ht4M7YKaCg4xvYlDgAAAAqklEQVR4AX3QRRKFQAwA0cwgwd3duf8Jv0ugKvT27RpOCQl8iqoJFnU0TMmihbbjAs0Tf7Qs9DWKQRAStFCNCMZJmhG0copFUiaVYPFR3Vxg24k3ot2HZyw/iOpAjSJavUaJ4mibEjiUEwCL79yQRTnZEYfubOUMCs23kEE5G2hZDIrF5hFAU/GIMUEInSPWFAFWlWJTJyU7AcItbQme84KdR2jqCwQRwqk7bagS0TTP5PcAAAAASUVORK5CYII=",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.sidebar.image("Hero_MotoCorp_Logo.png", use_column_width=True)


# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f4e79;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .section-header {
        background: linear-gradient(90deg, #1f4e79, #2e75b6);
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        font-weight: bold;
    }
    .status-ok {
        color: #28a745;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .status-not-ok {
        color: #dc3545;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .inspection-card {
        border: 2px solid #e9ecef;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f8f9fa;
    }
    .summary-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Workshop areas configuration
WORKSHOP_AREAS = {
    "Showroom- Frontage": {
        "description": "Showroom front facade and entry area",
        "criteria": ["Front Facade", "Parking Area", "Showroom Entry"]
    },
    "Showroom Elements- Inside view 1": {
        "description": "Interior view of showroom with design and reception elements",
        "criteria": ["Reception", "Colour Pallet", "Grey Lacquered Glass Wall"]
    },
    "Showroom Elements- Inside view 2": {
        "description": "Interior showroom view with merchandise and discussion zones",
        "criteria": ["Merchandise Wall", "Discussion Zone", "Display Zone"]
    },
    "Workshop- Reception Area": {
        "description": "Reception area within the workshop for customer interaction",
        "criteria": ["Reception backdrop", "Podium", "Tab & Printer"]
    },
    "Workshop- Floor Area with Manpower": {
        "description": "Workshop floor in use with technicians and tools",
        "criteria": ["Ramps with technician", "Equipments- Spark plug cleaner", "Battery charger"]
    },
    "Workshop- Washing Area": {
        "description": "Dedicated area for vehicle washing and drying",
        "criteria": ["Washing Pump", "Drying Area"]
    },
    "Workshop- Customer Lounge": {
        "description": "Lounge area for customers within the workshop",
        "criteria": ["Vision Wall", "TV", "Sofa", "AC"]
    },
    "Workshop- Spare Parts Area": {
        "description": "Area for storing and organizing spare parts",
        "criteria": ["Racks & Bins", "Initial Parts Kit & HGO"]
    },
    "Workshop- Special & General tools": {
        "description": "Section for storing and accessing tools used in the workshop",
        "criteria": ["Precision tools", "Diagnostic tools", "Special tools"]
    },
    "Workshop- Customer & Staff washroom": {
        "description": "Separate restrooms for customers and staff",
        "criteria": ["Separate washroom for HE/SHE"]
    }
}

def analyze_image(image, area_name, image_name):
    """
    Mock image analysis function - Replace with actual AI/ML model
    In production, you would integrate with:
    - Computer Vision APIs (Azure, AWS, Google)
    - Custom trained models
    - Rule-based image analysis
    """
    import random
    
    # Mock analysis based on image properties
    # You can replace this with actual image analysis logic
    try:
        # Simple mock logic - you can enhance this
        width, height = image.size
        file_size = len(image.tobytes())
        
        # Mock scoring based on image characteristics
        score = random.uniform(0.3, 1.0)  # Random score for demo
        
        # You can add more sophisticated logic here
        if width < 200 or height < 200:
            score *= 0.7  # Penalize very small images
        
        if file_size < 10000:
            score *= 0.8  # Penalize very small file sizes
        
        if any(x in image_name.lower() for x in ('not ok', 'not_ok', 'poor', 'bad', 'fail', "not")):
            score = 0.3

        elif any(x in image_name.lower() for x in ('ok', 'good', 'excellent')):
            score = 0.9

        return "OK" if score > 0.6 else "NOT OK", score
    except:
        return "NOT OK", 0.0

def initialize_session_state():
    """Initialize session state variables"""
    if 'inspection_results' not in st.session_state:
        st.session_state.inspection_results = {}
    if 'uploaded_images' not in st.session_state:
        st.session_state.uploaded_images = {}
    if 'inspection_date' not in st.session_state:
        st.session_state.inspection_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    initialize_session_state()
    
    # Header
    #st.markdown('<h1 class="main-header">🏍️ Dealer Activation Report Submission</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style='display: flex; align-items: center; gap: 10px;'>
        <img src='https://www.heromotocorp.com/content/dam/hero-aem-website/brand/logo/logo.svg' alt='Hero Logo' style='height: 50px;' />
        <h1 style='margin: 0;'>Dealer Activation Report Submission</h1>
    </div>
                """, unsafe_allow_html=True)
    # Sidebar
    with st.sidebar:
        st.markdown("### Inspection Dashboard")
        st.markdown(f"**Date:** {st.session_state.inspection_date}")
        
        # Progress tracking
        completed_sections = len([k for k, v in st.session_state.inspection_results.items() if v is not None])
        total_sections = len(WORKSHOP_AREAS)
        progress = completed_sections / total_sections
        
        st.progress(progress)
        st.markdown(f"**Progress:** {completed_sections}/{total_sections} sections completed")
        
        # Quick summary
        if completed_sections > 0:
            ok_count = len([k for k, v in st.session_state.inspection_results.items() if v and v[0] == "OK"])
            not_ok_count = completed_sections - ok_count
            
            st.markdown("### Quick Summary")
            st.markdown(f"✅ **OK:** {ok_count}")
            st.markdown(f"❌ **NOT OK:** {not_ok_count}")
        
        # Reset button
        if st.button("🔄 Reset All Inspections", type="secondary"):
            st.session_state.inspection_results = {}
            st.session_state.uploaded_images = {}
            st.session_state.inspection_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.rerun()
    
    # Main content
    st.markdown("### Upload image as per below checklist & get instant assessment")
    
    # Create tabs for better organization
    tab1, tab2 = st.tabs(["📷 Inspection Areas", "📊 Summary Report"])
    
    with tab1:
        # Create inspection sections
        for i, (area_name, area_info) in enumerate(WORKSHOP_AREAS.items(), 1):
            with st.container():
                st.markdown(f'<div class="section-header">{i}. {area_name}</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    #st.markdown(f"**Description:** {area_info['description']}")
                    st.markdown(f"**Key Criteria:** {', '.join(area_info['criteria'])}")
                    
                    # File uploader
                    uploaded_file = st.file_uploader(
                        f"Upload image for {area_name}",
                        type=['png', 'jpg', 'jpeg'],
                        key=f"uploader_{area_name}",
                        help=f"Upload a clear image of the {area_name.lower()}"
                    )
                    
                    # if uploaded_file is not None:
                    #     #continue
                    #     # Display uploaded image
                    #     image = Image.open(uploaded_file)
                    #     st.image(image, caption=f"{area_name} - Uploaded Image", width=100)
                        
                    #     # Store image in session state
                    #     st.session_state.uploaded_images[area_name] = image
                        
                    #     # Analyze image
                    #     with st.spinner(f"Analyzing {area_name}..."):
                    #         result, confidence = analyze_image(image, area_name)
                    #         st.session_state.inspection_results[area_name] = (result, confidence)
                
                with col2:
                    # Display results
                    if uploaded_file is not None:
                        # Display uploaded image
                        image_name = uploaded_file.name
                        image = Image.open(uploaded_file)
                        #st.image(image, caption=f"{area_name} - Uploaded Image", width=100)
                        st.image(image, width=150)

                        # Store image in session state
                        st.session_state.uploaded_images[area_name] = image

                        # Analyze image
                        with st.spinner(f"Analyzing {area_name}..."):
                            result, confidence = analyze_image(image, area_name, image_name)
                            st.session_state.inspection_results[area_name] = (result, confidence)
                            st.markdown(f'<div class="status-ok">✅ Image Uploaded</div>', unsafe_allow_html=True)

                    #else:
                        #st.info("📤 Upload an image to get assessment")

                    # Display inspection results

                    # if area_name in st.session_state.inspection_results:
                    #     result, confidence = st.session_state.inspection_results[area_name]
                        
                    #     if result == "OK":
                    #         st.markdown(f'<div class="status-ok">✅ Image Uploaded</div>', unsafe_allow_html=True)
                    #         st.success(f"Confidence: {confidence:.1%}")
                    #     else:
                    #         st.markdown(f'<div class="status-not-ok">❌ {result}</div>', unsafe_allow_html=True)
                    #         st.error(f"Confidence: {confidence:.1%}")
                        
                        # # Action buttons
                        # col_a, col_b = st.columns(2)
                        # with col_a:
                        #     if st.button(f"✅ Mark OK", key=f"ok_{area_name}", help="Override as OK"):
                        #         st.session_state.inspection_results[area_name] = ("OK", 1.0)
                        #         st.rerun()
                        # with col_b:
                        #     if st.button(f"❌ Mark NOT OK", key=f"not_ok_{area_name}", help="Override as NOT OK"):
                        #         st.session_state.inspection_results[area_name] = ("NOT OK", 1.0)
                        #         st.rerun()
                    # else:
                    #     st.info("📤 Upload an image to get assessment")
                
                st.markdown("---")
    
    with tab2:
        # Summary Report
        if st.session_state.inspection_results:
            st.markdown('<div class="summary-card">', unsafe_allow_html=True)
            st.markdown("## 📊 Inspection Summary Report")
            st.markdown(f"**Inspection Date:** {st.session_state.inspection_date}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Create summary dataframe
            summary_data = []
            for area_name, area_info in WORKSHOP_AREAS.items():
                if area_name in st.session_state.inspection_results:
                    result, confidence = st.session_state.inspection_results[area_name]
                    summary_data.append({
                        "Area": area_name,
                        "Status": result,
                        "Confidence": f"{confidence:.1%}",
                        #"Description": area_info['description']
                    })
                else:
                    summary_data.append({
                        "Area": area_name,
                        "Status": "Pending",
                        "Confidence": "-",
                        #"Description": area_info['description']
                    })
            
            df = pd.DataFrame(summary_data)
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_inspected = len([x for x in df['Status'] if x != 'Pending'])
                st.metric("Total Inspected", total_inspected)
            
            with col2:
                ok_count = len([x for x in df['Status'] if x == 'OK'])
                st.metric("✅ OK", ok_count)
            
            with col3:
                not_ok_count = len([x for x in df['Status'] if x == 'NOT OK'])
                st.metric("❌ NOT OK", not_ok_count)
            
            with col4:
                if total_inspected > 0:
                    compliance_rate = (ok_count / total_inspected) * 100
                    st.metric("Compliance Rate", f"{compliance_rate:.1f}%")
                else:
                    st.metric("Compliance Rate", "0%")
            
            # Display summary table
            st.markdown("### Detailed Results")
            
            # Style the dataframe
            def highlight_status(val):
                if val == 'OK':
                    return 'background-color: #d4edda; color: #155724'
                elif val == 'NOT OK':
                    return 'background-color: #f8d7da; color: #721c24'
                else:
                    return 'background-color: #fff3cd; color: #856404'
            
            styled_df = df.style.applymap(highlight_status, subset=['Status'])
            st.dataframe(styled_df, use_container_width=True)
            
            # Export functionality
            if st.button("📥 Export Report as CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV Report",
                    data=csv,
                    file_name=f"workshop_inspection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

            # Simulated Email Button
            if st.button("📧 Email Report"):
                with st.spinner("Sending email..."):
                    time.sleep(1)  # Simulate delay
                st.success("📤 Email sent successfully!")
            
            # Recommendations based on results
            st.markdown("### 🎯 Recommendations")
            not_ok_areas = [area for area, (status, _) in st.session_state.inspection_results.items() if status == "NOT OK"]
            
            if not_ok_areas:
                st.warning("**Areas requiring immediate attention:**")
                for area in not_ok_areas:
                    criteria = WORKSHOP_AREAS[area]['criteria']
                    st.markdown(f"- **{area}**: Focus on {', '.join(criteria[:2])}")
            else:
                st.success("🎉 Excellent! All inspected areas meet the quality standards.")
        
        else:
            st.info("📋 No inspection data available. Please upload images in the inspection areas tab.")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; margin-top: 2rem;'>
            <p>Two-Wheeler Workshop Inspection Tool v1.0 | Area Service Manager Dashboard</p>
            <p>For technical support, contact your IT administrator</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()