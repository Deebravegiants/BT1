# [H] DB-GPT Uncontrolled Resource Consumption vulnerability

## Summary
Severity: High
Advisory: GHSA-6xgj-c5fx-5v57
CVE: CVE-2024-10829
CWE: CWE-400, CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-6xgj-c5fx-5v57
Type: github-advisory

## Affected
- PyPI: `dbgpt` — affected >=0

## Details
A Denial of Service (DoS) vulnerability in the multipart request boundary processing mechanism of eosphoros-ai/db-gpt v0.6.0 allows unauthenticated attackers to cause excessive resource consumption. The server fails to handle excessive characters appended to the end of multipart boundaries, leading to an infinite loop and complete denial of service for all users. This vulnerability affects all endpoints processing multipart/form-data requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10829
- https://github.com/eosphoros-ai/DB-GPT
- https://huntr.com/bounties/e3a4a0ad-a2e0-497f-a2e0-e3c0ec7c4de4
