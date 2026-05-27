## ADDED Requirements

### Requirement: Classify travel intention
The system SHALL classify a user's travel-related query into one of several predefined categories (e.g., leisure, business, adventure) using zero-shot classification.

#### Scenario: Leisure travel intention
- **WHEN** a user submits a query like "I want to find a quiet cabin in the woods for a weekend getaway."
- **THEN** the system SHALL classify the intention as "leisure" or a similar category.

#### Scenario: Business travel intention
- **WHEN** a user submits a query like "I need to book a hotel near the convention center for my upcoming conference."
- **THEN** the system SHALL classify the intention as "business" or a similar category.
