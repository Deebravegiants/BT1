# [H] raspap-webgui vulnerable to denial of service

## Summary
Severity: High
Advisory: GHSA-vc9f-mgxr-h32r
CVE: CVE-2024-28754
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-09
Source: https://github.com/advisories/GHSA-vc9f-mgxr-h32r
Type: github-advisory

## Affected
- Packagist: `billz/raspap-webgui` — affected >=0 <3.1.0

## Details
RaspAP (aka raspap-webgui) through 3.0.9 allows remote attackers to cause a persistent denial of service (bricking) via a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28754
- https://github.com/RaspAP/raspap-webgui/pull/1546
- https://github.com/RaspAP/raspap-webgui/pull/1548
- https://github.com/RaspAP/raspap-webgui/commit/d0592b63de9a5da587ab3a51e03e7e566c7f3602
- https://dustri.org/b/carrot-disclosure.html
- https://github.com/RaspAP/raspap-webgui
