# [M] 5.1 Ineffective Try Catch Statement

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Risk Accepted

Try catch statements should handle critical code parts that might fail and their respective exertions
correctly. The used try catch statement in authorizationDecrease simple fails silently if not
successful. Resulting in potential incorrect authorization decrease.

Risk accepted :

Threshold Network accepts that a decrease fails silently. The event
AuthorizationInvoluntaryDecreased has been added to track involuntary decreases, it contains
a field to indicate whether the call to the application succeeded or not.
