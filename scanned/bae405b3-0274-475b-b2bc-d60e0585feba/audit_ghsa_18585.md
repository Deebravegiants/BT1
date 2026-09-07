# [M] MCMS reflected cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wvv5-5g6x-hp7j
CVE: CVE-2025-60837
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-23
Source: https://github.com/advisories/GHSA-wvv5-5g6x-hp7j
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=0

## Details
A reflected cross-site scripting (XSS) vulnerability in MCMS v6.0.1 allows attackers to execute arbitrary Javascript in the context of a user's browser via a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-60837
- https://gist.github.com/xuzhiwei66666666/5cec37c9f674a08bc0d8654d42b4137a
- https://gitee.com/mingSoft/MCMS
- https://github.com/ming-soft/MCMS
- http://mcms.com
