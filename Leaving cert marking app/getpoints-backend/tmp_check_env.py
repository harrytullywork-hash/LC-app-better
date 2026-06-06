from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).resolve().parent / '.env')
print('ANTHROPIC_API_KEY', bool(os.getenv('ANTHROPIC_API_KEY')))
print('AI_PROVIDER', os.getenv('AI_PROVIDER'))
print('DEMO_MODE', os.getenv('DEMO_MODE'))
