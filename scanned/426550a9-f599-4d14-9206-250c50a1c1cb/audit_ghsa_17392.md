# [M] 1Panel contains a cross-site request forgery (CSRF) vulnerability in the panel name management functionality

## Summary
Severity: Medium
Advisory: GHSA-5xpq-2vmc-5cqp
CVE: CVE-2025-34430
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-5xpq-2vmc-5cqp
Type: github-advisory

## Affected
- Go: `github.com/1Panel-dev/1Panel` — affected >=1.10.33

## Details
1Panel versions 1.10.33 through 2.0.15 contain a cross-site request forgery (CSRF) vulnerability in the panel name management functionality. The affected endpoint does not implement CSRF defenses such as anti-CSRF tokens or Origin/Referer validation. An attacker can craft a malicious webpage that submits a panel-name change request; if a victim visits the page while authenticated, the browser includes valid session cookies and the request succeeds. This allows a remote attacker to change the victim’s panel name to an arbitrary value without consent.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-34430
- https://1panel.pro
- https://github.com/1Panel-dev/1Panel
- https://github.com/1Panel-dev/1Panel/releases
- https://www.vulncheck.com/advisories/1panel-csrf-panel-name-modification
