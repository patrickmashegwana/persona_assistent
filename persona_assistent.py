import streamlit as st
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uuid
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -----------------------------------
# Basic Pydantic Models
# -----------------------------------
class CompanyData(BaseModel):
    name: str = "My Startup"
    description: str = "Cloud optimization services"
    location: str = "Berlin, Germany"
    ideal_income_eur: int = Field(40000, ge=0)
    geography: str = "EU"

class ClientData(BaseModel):
    name: str
    age: Optional[int]
    country: str
    job_title: Optional[str]
    annual_income_eur: Optional[float]
    interests: Optional[str]
    notes: Optional[str] = None

# -----------------------------------
# Initialize in-memory persona store
# -----------------------------------
if "personas" not in st.session_state:
    st.session_state.personas = []

# -----------------------------------
# Simple UI Header
# -----------------------------------
st.set_page_config(page_title="Personan Assistant", layout="wide")
st.title("Personan Assistant — Starter App")

st.markdown("This is a minimal starting point. Build on top of this.")

# Placeholder company object
company = CompanyData()

# Placeholder text block to confirm running
st.info("App initialized. Ready to add forms, scoring logic, and pitch generation.")
"working on this"