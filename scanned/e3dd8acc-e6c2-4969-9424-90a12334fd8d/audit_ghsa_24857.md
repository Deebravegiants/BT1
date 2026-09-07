# [M] MunkiReport Cross-Site Scripting (XSS) Filter Bypass On Comment

## Summary
Severity: Medium
Advisory: GHSA-vc4f-2g7f-pmqr
CVE: CVE-2020-15885
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vc4f-2g7f-pmqr
Type: github-advisory

## Affected
- Packagist: `munkireport/comment` — affected >=0 <4.0

## Details
A Cross-Site Scripting (XSS) vulnerability in the comment module before 4.0 for MunkiReport allows remote attackers to inject arbitrary web script or HTML by posting a new comment.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15885
- https://github.com/munkireport/comment/commit/ee4c1cd28fdcb42eb24c0cfea24ddf02478f9869
- https://github.com/munkireport/comment
- https://github.com/munkireport/comment/releases
- https://github.com/munkireport/munkireport-php
- https://github.com/munkireport/munkireport-php/releases/tag/v5.6.3
- https://github.com/munkireport/munkireport-php/wiki/20200722--XSS-Filter-Bypass-On-Comments
