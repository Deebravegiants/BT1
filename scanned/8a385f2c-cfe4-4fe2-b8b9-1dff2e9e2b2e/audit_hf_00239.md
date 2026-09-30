# [H] Unrestricted vestFor

## Summary
Severity: High
Contest weight: 0.0994
Dataset id: 1238
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Anyone can call function `vestFor` and block any user with a tiny amount of Vader. This function has no auth checks so a malicious actor can front-run legit `vestFor` calls with insignificant amounts. This function locks the user for 365 days and does not allow updating the value, thus forbids legit conversions.

## Recommendation
Consider introducing a whitelist of callers that can vest on behalf of others (e.g. Converter).
