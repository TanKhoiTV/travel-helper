## ADDED Requirements

### Requirement: Identify topics in reviews
The system SHALL identify the key topics or themes mentioned within a user review using zero-shot classification.

#### Scenario: Detecting multiple topics
- **WHEN** a user submits a review like "The food was delicious, but the service was quite slow."
- **THEN** the system SHALL identify both "food & dining" and "customer service" as relevant topics.
