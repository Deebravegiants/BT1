# [H] Open WebUI Unauthenticated Multipart Boundary Denial of Service (DoS) Vulnerability

## Summary
Severity: High
Advisory: GHSA-5ccf-884p-4jjq
CWE: CWE-400
Ecosystem: PyPI, npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-5ccf-884p-4jjq
Type: github-advisory

## Affected
- npm: `open-webui` — affected >=0
- PyPI: `open-webui` — affected >=0

## Details
A Denial of Service (DoS) vulnerability exists in open-webui/open-webui version 0.3.21. This vulnerability affects multiple endpoints, including `/ollama/models/upload`, `/audio/api/v1/transcriptions`, and `/rag/api/v1/doc`. The application processes multipart boundaries without authentication, leading to resource exhaustion. By appending additional characters to the multipart boundary, an attacker can cause the server to parse each byte of the boundary, ultimately leading to service unavailability. This vulnerability can be exploited remotely, resulting in high CPU and memory usage, and rendering the service inaccessible to legitimate users.

## References
- https://github.com/Kludex/python-multipart/security/advisories/GHSA-59g5-xgcq-4qw3
- https://nvd.nist.gov/vuln/detail/CVE-2024-53981
- https://github.com/open-webui/open-webui
- https://huntr.com/bounties/9178f09e-4d4f-4a5b-bc32-cada7445b03c
