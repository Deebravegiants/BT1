# [M] SQL injection in litellm

## Summary
Severity: Medium
Advisory: GHSA-8j42-pcfm-3467
CVE: CVE-2024-4890
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-06
Source: https://github.com/advisories/GHSA-8j42-pcfm-3467
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=0

## Details
A blind SQL injection vulnerability exists in the berriai/litellm application, specifically within the '/team/update' process. The vulnerability arises due to the improper handling of the 'user_id' parameter in the raw SQL query used for deleting users. An attacker can exploit this vulnerability by injecting malicious SQL commands through the 'user_id' parameter, leading to potential unauthorized access to sensitive information such as API keys, user information, and tokens stored in the database. The affected version is 1.27.14.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4890
- https://github.com/BerriAI/litellm/pull/2954
- https://github.com/BerriAI/litellm
- https://huntr.com/bounties/a4f6d357-5b44-4e00-9cac-f1cc351211d2
