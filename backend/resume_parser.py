import re
import markdown
from bs4 import BeautifulSoup
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ResumeParser:
    def __init__(self):
        self.section_patterns = {
            'name': r'^#\s+(.+)$',
            'title': r'^##\s+(.+)$',
            'summary': r'^###\s+Summary\s*\n(.+?)(?=^###|\Z)',
            'education': r'^###\s+Education\s*\n(.+?)(?=^###|\Z)',
            'skills': r'^###\s+Skills\s*\n(.+?)(?=^###|\Z)',
            'projects': r'^###\s+Projects\s*\n(.+?)(?=^###|\Z)',
            'certifications': r'^###\s+Certifications\s*\n(.+?)(?=^###|\Z)',
            'languages': r'^###\s+Languages\s*\n(.+?)(?=^###|\Z)'
        }

    def parse_markdown_to_json(self, markdown_text: str) -> Dict:
        """
        Parse markdown resume text into structured JSON.
        
        Args:
            markdown_text: Resume text in markdown format
            
        Returns:
            Dict: Structured resume data
        """
        try:
            # Convert markdown to HTML
            html = markdown.markdown(markdown_text)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Initialize result dictionary
            result = {}
            
            # Extract name and title
            h1 = soup.find('h1')
            if h1:
                result['name'] = h1.text.strip()
            
            h2 = soup.find('h2')
            if h2:
                result['title'] = h2.text.strip()
            
            # Extract summary
            summary_section = soup.find('h3', text='Summary')
            if summary_section:
                summary_text = []
                current = summary_section.find_next_sibling()
                while current and current.name != 'h3':
                    if current.name == 'p':
                        summary_text.append(current.text.strip())
                    current = current.find_next_sibling()
                result['summary'] = ' '.join(summary_text)
            
            # Extract education
            education_section = soup.find('h3', text='Education')
            if education_section:
                result['education'] = self._parse_education(education_section)
            
            # Extract skills
            skills_section = soup.find('h3', text='Skills')
            if skills_section:
                result['skills'] = self._parse_list(skills_section)
            
            # Extract projects
            projects_section = soup.find('h3', text='Projects')
            if projects_section:
                result['projects'] = self._parse_projects(projects_section)
            
            # Extract certifications
            certs_section = soup.find('h3', text='Certifications')
            if certs_section:
                result['certifications'] = self._parse_certifications(certs_section)
            
            # Extract languages
            languages_section = soup.find('h3', text='Languages')
            if languages_section:
                result['languages'] = self._parse_list(languages_section)
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            raise

    def _parse_education(self, section) -> List[Dict]:
        education = []
        current = section.find_next_sibling()
        while current and current.name != 'h3':
            if current.name == 'ul':
                for li in current.find_all('li'):
                    text = li.text.strip()
                    # Parse education entry
                    parts = text.split(' - ')
                    if len(parts) >= 2:
                        institution = parts[0].strip()
                        details = parts[1].strip()
                        year_range = re.search(r'\((\d{4}-\d{4}|\d{4})\)', details)
                        if year_range:
                            year_range = year_range.group(1)
                            details = details.replace(f'({year_range})', '').strip()
                        
                        education.append({
                            'institution': institution,
                            'degree': details,
                            'year_range': year_range or ''
                        })
            current = current.find_next_sibling()
        return education

    def _parse_list(self, section) -> List[str]:
        items = []
        current = section.find_next_sibling()
        while current and current.name != 'h3':
            if current.name == 'ul':
                for li in current.find_all('li'):
                    items.append(li.text.strip())
            current = current.find_next_sibling()
        return items

    def _parse_projects(self, section) -> List[Dict]:
        projects = []
        current = section.find_next_sibling()
        while current and current.name != 'h3':
            if current.name == 'ul':
                for li in current.find_all('li'):
                    text = li.text.strip()
                    parts = text.split(': ', 1)
                    if len(parts) == 2:
                        projects.append({
                            'name': parts[0].strip(),
                            'description': parts[1].strip()
                        })
            current = current.find_next_sibling()
        return projects

    def _parse_certifications(self, section) -> List[Dict]:
        certifications = []
        current = section.find_next_sibling()
        while current and current.name != 'h3':
            if current.name == 'ul':
                for li in current.find_all('li'):
                    text = li.text.strip()
                    # Parse certification entry
                    parts = text.split(' - ')
                    if len(parts) >= 2:
                        title = parts[0].strip()
                        issuer_date = parts[1].strip()
                        date_match = re.search(r'\((\d{4})\)', issuer_date)
                        if date_match:
                            date = date_match.group(1)
                            issuer = issuer_date.replace(f'({date})', '').strip()
                            certifications.append({
                                'title': title,
                                'issuer': issuer,
                                'date': date
                            })
            current = current.find_next_sibling()
        return certifications 