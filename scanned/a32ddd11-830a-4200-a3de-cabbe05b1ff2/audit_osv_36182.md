# [H] Flag Forge has ReDoS Vulnerability in User Profile Lookup API

## Summary
Severity: High
Advisory: CVE-2026-21868
Aliases: GHSA-949h-9824-xmcx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/CVE-2026-21868
Type: osv

## Details
Flag Forge is a Capture The Flag (CTF) platform. Versions 2.3.2 and below have a Regular Expression Denial of Service (ReDoS) vulnerability in the user profile API endpoint (/api/user/[username]). The application constructs a regular expression dynamically using unescaped user input (the username parameter). An attacker can exploit this by sending a specially crafted username containing regex meta-characters (e.g., deeply nested groups or quantifiers), causing the MongoDB regex engine to consume excessive CPU resources. This can lead to Denial of Service for other users. The issue is fixed in version 2.3.3. To workaround this issue, implement a Web Application Firewall (WAF) rule to block requests containing regex meta-characters in the URL path.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21868.json
- https://github.com/FlagForgeCTF/flagForge/security/advisories/GHSA-949h-9824-xmcx
- https://nvd.nist.gov/vuln/detail/CVE-2026-21868
