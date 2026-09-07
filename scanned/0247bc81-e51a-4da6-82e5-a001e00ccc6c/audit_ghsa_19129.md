# [M]  Leantime has Insufficiently Protected Credentials

## Summary
Severity: Medium
Advisory: GHSA-h6w8-27ph-c385
CWE: CWE-522
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-21
Source: https://github.com/advisories/GHSA-h6w8-27ph-c385
Type: github-advisory

## Affected
- Packagist: `leantime/leantime` — affected >=0 <3.3

## Details
Due to improper cache control an attacker can view sensitive information even if they are not logged into the account anymore.

Additional Information:

    1.The issue was identified during routine security testing.
    2.This vulnerability poses a significant risk to user privacy and data security.
    3.Urgent action is recommended to mitigate this vulnerability and protect user data from unauthorized access.

## References
- https://github.com/Leantime/leantime/security/advisories/GHSA-h6w8-27ph-c385
- https://github.com/Leantime/leantime
