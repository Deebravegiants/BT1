# [M] Open Redirect in Caddy

## Summary
Severity: Medium
Advisory: GHSA-qpm3-vr34-h8w8
CVE: CVE-2022-28923
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-07
Source: https://github.com/advisories/GHSA-qpm3-vr34-h8w8
Type: github-advisory

## Affected
- Go: `github.com/caddyserver/caddy/v2` — affected >=0 <2.5.0-beta.1

## Details
Caddy v2.4.6 was discovered to contain an open redirection vulnerability which allows attackers to redirect users to phishing websites via crafted URLs

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28923
- https://github.com/caddyserver/caddy/commit/78b5356f2b1945a90de1ef7f2c7669d82098edbd
- https://github.com/caddyserver/caddy
- https://lednerb.de/en/publications/responsible-disclosure/caddy-open-redirect-vulnerability
- https://pkg.go.dev/vuln/GO-2023-1567
