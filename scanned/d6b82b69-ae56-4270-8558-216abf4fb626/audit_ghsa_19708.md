# [H] imaginAIry Denial of Service (DoS) vulnerability

## Summary
Severity: High
Advisory: GHSA-x5xw-28w4-53j5
CVE: CVE-2024-12761
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-x5xw-28w4-53j5
Type: github-advisory

## Affected
- PyPI: `imaginAIry` — affected >=0

## Details
A Denial of Service (DoS) vulnerability exists in the brycedrennan/imaginairy repository, version 15.0.0. The vulnerability is present in the `/api/stablestudio/generate` endpoint, which can be exploited by sending an invalid request. This causes the server process to terminate abruptly, outputting `KILLED` in the terminal, and results in the unavailability of the server. This issue disrupts the server's functionality, affecting all users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-12761
- https://github.com/brycedrennan/imaginAIry
- https://huntr.com/bounties/282900f4-2498-42c4-8ce7-ba5368aaf035
