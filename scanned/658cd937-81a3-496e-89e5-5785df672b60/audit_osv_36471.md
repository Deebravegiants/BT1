# [M] WeGIA Clickjacking Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2026-23731
Aliases: GHSA-99qp-hjvh-c59q
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2026-01-16
Source: https://osv.dev/vulnerability/CVE-2026-23731
Type: osv

## Details
WeGIA is a web manager for charitable institutions. Prior to 3.6.2, The web application is vulnerable to clickjacking attacks. The WeGIA application does not send any defensive HTTP headers related to framing protection. In particular, X-Frame-Options is missing andContent-Security-Policy with frame-ancestors directive is not configured. Because of this, an attacker can load any WeGIA page inside a malicious HTML document, overlay deceptive elements, hide real buttons, or force accidental interaction with sensitive workflows. This vulnerability is fixed in 3.6.2.

## References
- https://github.com/LabRedesCefetRJ/WeGIA/releases/tag/3.6.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23731.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-99qp-hjvh-c59q
- https://nvd.nist.gov/vuln/detail/CVE-2026-23731
- https://github.com/LabRedesCefetRJ/WeGIA/pull/1333
