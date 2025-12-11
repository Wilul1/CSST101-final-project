from datetime import datetime
import re

class KRREngine:
    """Knowledge Representation and Reasoning Engine for advisory recommendations"""
    
    def __init__(self):
        self.rules = self._initialize_rules()
    
    def _initialize_rules(self):
        """Initialize rule base"""
        return [
            {
                'name': 'Streetlight Dangerous',
                'conditions': [
                    lambda cat, desc, loc: cat == 'Streetlight issue',
                    lambda cat, desc, loc: any(word in desc.lower() for word in ['dangerous', 'dark', 'no light', 'no lights', 'broken', 'safety'])
                ],
                'action': 'Dispatch repair team within 24 hours. High safety priority.',
                'priority': 'High'
            },
            {
                'name': 'Waste Overflowing',
                'conditions': [
                    lambda cat, desc, loc: cat == 'Waste collection',
                    lambda cat, desc, loc: any(word in desc.lower() for word in ['overflowing', 'overflow', 'blocking', 'blocked', 'health'])
                ],
                'action': 'Send garbage collection team immediately. Health hazard detected.',
                'priority': 'High'
            },
            {
                'name': 'Road Accident Risk',
                'conditions': [
                    lambda cat, desc, loc: cat == 'Road repair',
                    lambda cat, desc, loc: any(word in desc.lower() for word in ['accident', 'dangerous', 'urgent', 'immediate', 'pothole', 'damage'])
                ],
                'action': 'Prioritize road repair team. Safety risk identified.',
                'priority': 'High'
            },
            {
                'name': 'Water Emergency',
                'conditions': [
                    lambda cat, desc, loc: cat == 'Water service issue',
                    lambda cat, desc, loc: any(word in desc.lower() for word in ['burst', 'flood', 'flooding', 'leak', 'emergency', 'urgent'])
                ],
                'action': 'Dispatch water service team immediately. Emergency situation.',
                'priority': 'High'
            },
            {
                'name': 'Streetlight Night Time',
                'conditions': [
                    lambda cat, desc, loc: cat == 'Streetlight issue',
                    lambda cat, desc, loc: self._is_night_time()
                ],
                'action': 'Immediate dispatch recommended due to night time conditions.',
                'priority': 'High'
            },
            {
                'name': 'Waste High Frequency',
                'conditions': [
                    lambda cat, desc, loc: cat == 'Waste collection',
                    lambda cat, desc, loc: self._check_location_frequency(loc) > 2
                ],
                'action': 'Multiple reports from this area. Prioritize clean-up team.',
                'priority': 'Medium'
            },
            {
                'name': 'Noise Night Time',
                'conditions': [
                    lambda cat, desc, loc: cat == 'Noise complaint',
                    lambda cat, desc, loc: self._is_night_time()
                ],
                'action': 'Noise complaint during night hours. Send inspection team.',
                'priority': 'Medium'
            },
            {
                'name': 'Standard Streetlight',
                'conditions': [
                    lambda cat, desc, loc: cat == 'Streetlight issue'
                ],
                'action': 'Schedule maintenance team for streetlight repair.',
                'priority': 'Medium'
            },
            {
                'name': 'Standard Waste',
                'conditions': [
                    lambda cat, desc, loc: cat == 'Waste collection'
                ],
                'action': 'Schedule regular garbage collection.',
                'priority': 'Medium'
            },
            {
                'name': 'Standard Road',
                'conditions': [
                    lambda cat, desc, loc: cat == 'Road repair'
                ],
                'action': 'Add to road maintenance schedule.',
                'priority': 'Medium'
            },
            {
                'name': 'Graffiti Standard',
                'conditions': [
                    lambda cat, desc, loc: cat == 'Graffiti removal'
                ],
                'action': 'Schedule graffiti removal team.',
                'priority': 'Low'
            },
            {
                'name': 'General Inquiry',
                'conditions': [
                    lambda cat, desc, loc: cat == 'Others'
                ],
                'action': 'Forward to appropriate department for review.',
                'priority': 'Low'
            }
        ]
    
    def _is_night_time(self):
        """Check if current time is night (6 PM - 6 AM)"""
        current_hour = datetime.now().hour
        return current_hour >= 18 or current_hour < 6
    
    def _check_location_frequency(self, location):
        """Check frequency of reports from same location (simplified)"""
        # In a real system, this would query the database
        # For now, return a mock value
        return 0
    
    def get_advisory(self, category, description, location):
        """Get advisory recommendation based on rules"""
        # Try to match rules in priority order (High priority rules first)
        sorted_rules = sorted(self.rules, key=lambda r: ['High', 'Medium', 'Low'].index(r['priority']))
        
        for rule in sorted_rules:
            if all(condition(category, description, location) for condition in rule['conditions']):
                return rule['action']
        
        # Default advisory if no rule matches
        return f"Standard processing for {category} request. Review and assign to appropriate team."
    
    def add_rule(self, name, conditions, action, priority='Medium'):
        """Add a new rule to the rule base"""
        self.rules.append({
            'name': name,
            'conditions': conditions,
            'action': action,
            'priority': priority
        })
    
    def get_all_rules(self):
        """Get all rules (for admin/debugging)"""
        return self.rules


