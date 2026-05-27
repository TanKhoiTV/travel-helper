## ADDED Requirements

### Requirement: Analyze user review sentiment
The system SHALL classify the sentiment of a user-provided review text as either POSITIVE or NEGATIVE using a text classification model.

#### Scenario: Positive review
- **WHEN** a user submits a review such as "The hotel was amazing and the staff was very friendly!"
- **THEN** the system SHALL return a sentiment classification of POSITIVE with a high confidence score.

#### Scenario: Negative review
- **WHEN** a user submits a review such as "The room was dirty and the service was terrible."
- **THEN** the system SHALL return a sentiment classification of NEGATIVE with a high confidence score.
