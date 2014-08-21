"""Run app in development
"""

import config
from app import create_app

app = create_app(config)
app.run()
