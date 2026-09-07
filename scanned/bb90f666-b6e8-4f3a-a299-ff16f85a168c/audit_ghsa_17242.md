# [H] 1Panel contains a cross-site request forgery (CSRF) vulnerability in the Change Username functionality

## Summary
Severity: High
Advisory: GHSA-rpr2-4hqj-hc4q
CVE: CVE-2025-34410
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-rpr2-4hqj-hc4q
Type: github-advisory

## Affected
- Go: `github.com/1Panel-dev/1Panel` — affected >=1.10.33

## Details
1Panel versions 1.10.33 - 2.0.15 contain a cross-site request forgery (CSRF) vulnerability in the Change Username functionality available from the settings panel (/settings/panel). The endpoint does not implement CSRF protections such as anti-CSRF tokens or Origin/Referer validation. An attacker can craft a malicious webpage that submits a username-change request; when a victim visits the page while authenticated, the browser includes valid session cookies and the request succeeds. This allows an attacker to change the victim’s 1Panel username without consent. After the change, the victim is logged out and unable to log in with the previous username, resulting in account lockout and denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-34410
- https://1panel.pro
- https://github.com/1Panel-dev/1Panel
- https://github.com/1Panel-dev/1Panel/releases
- https://www.vulncheck.com/advisories/1panel-csrf-in-change-username-functionality-allows-account-lockout
