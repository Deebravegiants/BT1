# [H] Unrestricted vestFor

## Summary
Severity: High
Chain: Smart contract
Component: 2021-11-vader
Published: 2021-11-15
Source: https://github.com/code-423n4/2021-11-vader-findings/issues/229
Type: code-finding

## Details
# Handle

pauliax


# Vulnerability details

## Impact
Anyone can call function vestFor and block any user with a tiny amount of Vader. This function has no auth checks so a malicious actor can front-run legit vestFor calls with insignificant amounts. This function locks the user for 365 days and does not allow updating the value, thus forbids legit conversions.

## Recommended Mitigation Steps
Consider introducing a whitelist of callers that can vest on behalf of others (e.g. Converter).
