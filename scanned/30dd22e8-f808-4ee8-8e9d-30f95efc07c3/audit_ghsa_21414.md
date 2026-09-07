# [C] SQL injection in Dolibarr

## Summary
Severity: Critical
Advisory: GHSA-gjg7-qfvp-9hm4
CVE: CVE-2022-4093
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-gjg7-qfvp-9hm4
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=16.0.1 <16.0.3

## Details
SQL injection attacks can result in unauthorized access to sensitive data, such as passwords, credit card details, or personal user information. Many high-profile data breaches in recent years have been the result of SQL injection attacks, leading to reputational damage and regulatory fines. In some cases, an attacker can obtain a persistent backdoor into an organization's systems, leading to a long-term compromise that can go unnoticed for an extended period. This affect 16.0.1 and 16.0.2 only. 16.0.0 or lower, and 16.0.3 or higher are not affected

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4093
- https://github.com/dolibarr/dolibarr/commit/7c1eac9774bd1fed0b7b4594159f2ac2d12a4011
- https://huntr.dev/bounties/677ca8ee-ffbc-4b39-b294-2ce81bd56788
