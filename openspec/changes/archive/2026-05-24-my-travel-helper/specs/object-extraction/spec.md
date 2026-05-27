## ADDED Requirements

### Requirement: Extract entities from text
The system SHALL identify and extract key entities (such as locations, dates, and organizations) from user-provided text using token classification (NER).

#### Scenario: Extracting locations and dates
- **WHEN** a user submits text like "I am traveling to Paris on June 15th."
- **THEN** the system SHALL extract "Paris" as a location (LOC) and "June 15th" as a date/time entity.
