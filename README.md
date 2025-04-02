PyBrowser is a full-featured web browser built with Python and PyQt5, designed to combine web browsing with powerful productivity tools. I created this to have a customizable browser that integrates my most-used utilities directly into the browsing experience.

🚀 Key Features
Core Browser Functionality
Tabbed browsing with intuitive controls

URL normalization (auto-adds https:// etc.)

Navigation buttons (back/forward/home)

Bookmark management with star indicator

Browsing history with timestamps

Integrated Productivity Tools
YouTube video downloader (one-click access)

Chess analyzer (opens as overlay)

AI chat assistant (custom implementation)

Lil' Helper integration (utility toolbox)

System monitoring tools

UI/UX Features
Modern dark theme (qtmodern styles)

Compact title bar with window controls

Quick-access tools menu

Bookmarks/history sidebar

💻 Technical Implementation
Browser Engine
python
Copy
class HtmlView(QWebEngineView):
    def __init__(self, main_window):
        super().__init__()
        self.setPage(WebEnginePage(self))
        self.load(QUrl("https://google.com")) 
        self.titleChanged.connect(self.update_tab_name)
        self.urlChanged.connect(self.update_url_input)
Tab Management
python
Copy
def new_tab(self):
    # Create tab with navigation controls
    tab = QWidget()
    browser_view = HtmlView(self)
    
    # Add to tab widget
    self.tab_widget.addTab(tab, 'New Tab')
    self.tab_widget.setCurrentWidget(tab)
    
    return browser_view
URL Handling
python
Copy
def current_tab_load_url(self):
    url_text = self.current_url_input().text().strip()
    
    # Auto-complete URL formats
    if not url_text.startswith(('http://', 'https://')):
        url_text = f'https://www.{url_text}'
        
    self.current_view().load(QUrl(url_text))
🛠️ Skills Demonstrated
Core Development

PyQt5/QWebEngineWidgets mastery

Custom browser engine implementation

Complex UI state management

System Integration

Inter-process communication

External tool integration (chess, AI, utilities)

File I/O for history/bookmarks

Problem Solving

Memory management for multiple tabs

URL normalization and validation

Responsive UI during page loads

🔧 Technical Highlights
Custom WebEnginePage

Overrides navigation handling for better control

Enables proper tabbed browsing behavior

Tool Integration System

python
Copy
self.menubtn.addAction("Chess", self.showchessscr)
self.menubtn.addAction("Chat", self.showchatwid) 
self.menubtn.addAction("LilHelper", self.showtreeview)
Smart URL Detection

Auto-shows/hides YouTube download button

Visual bookmark status indicator

🎨 UI/UX Design
Browser UI Layout
Clean interface with all controls accessible in one row

🚴‍♂️ Performance Optimizations
Lazy loading for tool windows

Efficient history/bookmark storage

Minimal resource usage when idle

🔮 Future Roadmap
Add extension system

Implement sync across devices

Enhance security features

Add reader mode

bash
Copy
# Run the browser
python pybrowser.py
This project showcases my ability to:

Build complex desktop applications in Python

Integrate multiple systems into cohesive products

Solve real-world usability challenges

Create polished, user-friendly interfaces
