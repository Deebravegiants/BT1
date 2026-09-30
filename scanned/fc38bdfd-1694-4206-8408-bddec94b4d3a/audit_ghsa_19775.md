# [H] FastChat Denial of Service vulnerability

## Summary
Severity: High
Advisory: GHSA-79rp-v9rm-gxm8
CVE: CVE-2024-10912
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-79rp-v9rm-gxm8
Type: github-advisory

## Affected
- PyPI: `fschat` — affected >=0

## Details
A Denial of Service (DoS) vulnerability exists in the file upload feature of lm-sys/fastchat version 0.2.36. The vulnerability is due to improper handling of form-data with a large filename in the file upload request. An attacker can exploit this by sending a payload with an excessively large filename, causing the server to become overwhelmed and unavailable to legitimate users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10912
- https://github.com/lm-sys/FastChat
- https://huntr.com/bounties/52f335b8-1134-4d0f-acb4-efef516de414
