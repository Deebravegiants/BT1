# [M] A refund is sent to recipient

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

When a refund is sent, it's sent to `recipient`. In case if a user wants to keep game items and money separate, it makes sense to send a refund back to `from` address. 

#### Recommendation

Since there may be different use cases, consider adding `refundAddress` to order structure.
