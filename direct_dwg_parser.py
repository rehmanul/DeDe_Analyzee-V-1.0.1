import streamlit as st
import os
import json
import plotly.graph_objects as go
from pathlib import Path
from shapely.geometry import Polygon
from enhanced_dwg_parser import parse_dwg_with_enhanced_parser
from datetime import datetime

st.set_page_config(page_title="Direct DWG Parser", layout="wide")

def parse_dwg_file(file_path):
    """Parse DWG file and extract room data using enhanced parser"""
    try:
        # Use enhanced DWG parser
        zones = parse_dwg_with_enhanced_parser(file_path)
        
        # Convert to expected format
        results = {
            'layers': list(set([zone.get('layer', 'Unknown') for zone in zones])),
            'entities': {'ROOMS': len(zones)},
            'rooms': []
        }
        
        # Convert zones to rooms format
        for zone in zones:
            if 'points' in zone and len(zone['points']) >= 3:
                try:
                    area = zone.get('area', abs(Polygon(zone['points']).area))
                    perimeter = Polygon(zone['points']).length
                    
                    results['rooms'].append({
                        'points': zone['points'],
                        'area': area,
                        'layer': zone.get('layer', 'Unknown'),
                        'perimeter': perimeter,
                        'type': zone.get('type', 'Unknown'),
                        'source': zone.get('source', 'parsed')
                    })
                except Exception:
                    # If shapely fails, calculate basic area
                    area = zone.get('area', 0)
                    results['rooms'].append({
                        'points': zone['points'],
                        'area': area,
                        'layer': zone.get('layer', 'Unknown'),
                        'perimeter': 0,
                        'type': zone.get('type', 'Unknown'),
                        'source': zone.get('source', 'parsed')
                    })
        
        return results
        
    except Exception as e:
        return {'error': str(e)}

def create_room_visualization(rooms):
    """Create plotly visualization of rooms"""
    fig = go.Figure()
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
    
    for i, room in enumerate(rooms):
        points = room['points']
        x = [p[0] for p in points] + [points[0][0]]
        y = [p[1] for p in points] + [points[0][1]]
        
        fig.add_trace(go.Scatter(
            x=x, y=y,
            fill='toself',
            fillcolor=colors[i % len(colors)],
            line=dict(color='black', width=1),
            name=f"Room {i+1} ({room['area']:.1f})",
            opacity=0.7
        ))
    
    fig.update_layout(
        title="Room Layout from DWG",
        xaxis_title="X Coordinate",
        yaxis_title="Y Coordinate",
        showlegend=True,
        yaxis=dict(scaleanchor="x", scaleratio=1)
    )
    return fig

st.title("Direct DWG File Parser")
st.write("Place your DWG/DXF files in the 'sample_files' directory and select them below.")

# Create sample files directory
sample_dir = Path("sample_files")
sample_dir.mkdir(exist_ok=True)

# Check for existing files
dwg_files = list(sample_dir.glob("*.dwg")) + list(sample_dir.glob("*.dxf"))

if dwg_files:
    st.success(f"Found {len(dwg_files)} DWG/DXF files")
    
    # File selector
    selected_file = st.selectbox(
        "Select file to analyze:",
        options=[f.name for f in dwg_files]
    )
    
    if selected_file and st.button("Analyze Selected File"):
        file_path = sample_dir / selected_file
        
        with st.spinner("Parsing DWG file..."):
            results = parse_dwg_file(str(file_path))
        
        if 'error' in results:
            st.error(f"Error parsing file: {results['error']}")
        else:
            st.success("File parsed successfully!")
            
            # Display results
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("File Information")
                st.write(f"**File:** {selected_file}")
                st.write(f"**Layers:** {len(results['layers'])}")
                
                st.subheader("Entities Found")
                for entity_type, count in results['entities'].items():
                    st.write(f"- {entity_type}: {count}")
                
                st.subheader("Rooms Detected")
                st.write(f"Total rooms: {len(results['rooms'])}")
                
                if results['rooms']:
                    for i, room in enumerate(results['rooms']):
                        st.write(f"Room {i+1}:")
                        st.write(f"  - Area: {room['area']:.2f}")
                        st.write(f"  - Layer: {room['layer']}")
            
            with col2:
                if results['rooms']:
                    st.subheader("Room Visualization")
                    fig = create_room_visualization(results['rooms'])
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No rooms detected in this file")
            
            # Export data
            st.subheader("Export Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # JSON Export
                export_data = json.dumps(results, indent=2, default=str)
                st.download_button(
                    label="📄 Download JSON Report",
                    data=export_data,
                    file_name=f"{selected_file.replace('.dwg', '').replace('.dxf', '')}_analysis.json",
                    mime="application/json"
                )
            
            with col2:
                # CSV Export for rooms
                if results['rooms']:
                    import io
                    csv_buffer = io.StringIO()
                    csv_buffer.write("Room,Area,Layer,Type,Source\n")
                    
                    for i, room in enumerate(results['rooms']):
                        csv_buffer.write(f"Room {i+1},{room['area']:.2f},{room['layer']},{room.get('type', 'Unknown')},{room.get('source', 'parsed')}\n")
                    
                    csv_data = csv_buffer.getvalue()
                    
                    st.download_button(
                        label="📊 Download CSV Report",
                        data=csv_data,
                        file_name=f"{selected_file.replace('.dwg', '').replace('.dxf', '')}_rooms.csv",
                        mime="text/csv"
                    )
            
            with col3:
                # Summary Text Export
                summary_text = f"""DWG Analysis Report
==================
File: {selected_file}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

File Information:
- Layers: {len(results['layers'])}
- Total Rooms: {len(results['rooms'])}

Room Details:
"""
                
                for i, room in enumerate(results['rooms']):
                    summary_text += f"""
Room {i+1}:
  - Area: {room['area']:.2f} sq units
  - Layer: {room['layer']}
  - Type: {room.get('type', 'Unknown')}
  - Points: {len(room['points'])} vertices
"""
                
                summary_text += f"""
Analysis Generated By: Enhanced DWG Parser
Total Floor Area: {sum(room['area'] for room in results['rooms']):.2f} sq units
"""
                
                st.download_button(
                    label="📝 Download Summary",
                    data=summary_text,
                    file_name=f"{selected_file.replace('.dwg', '').replace('.dxf', '')}_summary.txt",
                    mime="text/plain"
                )

else:
    st.info("No DWG/DXF files found in the sample_files directory.")
    st.write("To use this parser:")
    st.write("1. Copy your DWG/DXF files to the 'sample_files' folder")
    st.write("2. Refresh this page")
    st.write("3. Select and analyze your files")

# Alternative: Text input for file path
st.subheader("Or specify file path directly")
file_path_input = st.text_input("Enter full path to DWG/DXF file:")

if file_path_input and st.button("Parse from Path"):
    if os.path.exists(file_path_input):
        results = parse_dwg_file(file_path_input)
        if 'error' not in results:
            st.success("File parsed successfully!")
            st.json(results)
        else:
            st.error(results['error'])
    else:
        st.error("File not found")

# Show current directory structure
with st.expander("Debug: Show Directory Structure"):
    st.write(f"Current directory: {os.getcwd()}")
    st.write(f"Sample directory: {sample_dir.absolute()}")
    st.write("Files in sample_files:")
    for f in sample_dir.iterdir():
        st.write(f"- {f.name} ({f.stat().st_size} bytes)")