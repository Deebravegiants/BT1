# [H] Atlantis GitHub App Setup Endpoint Returns App Credentials to Unauthenticated Callers

## Summary
Severity: High
Advisory: CVE-2026-82282
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82282
Type: osv

## Details
Atlantis through 0.47.1 fails to authenticate the /github-app/setup endpoint, allowing unauthenticated attackers to access GitHub App credentials. Attackers can observe or intercept the GitHub redirect during setup to obtain the RSA private key and webhook secret, enabling installation token minting and webhook payload forgery.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82282.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82282
- https://www.vulncheck.com/advisories/atlantis-github-app-setup-endpoint-returns-app-credentials-to-unauthenticated-callers
- https://github.com/runatlantis/atlantis/issues/6622
- https://github.com/runatlantis/atlantis
- https://github.com/runatlantis/atlantis/blob/12bfa59f44d8f65bfdda132bff61d8f8f29af1d6/server/controllers/github_app_controller.go
- https://github.com/runatlantis/atlantis/blob/12bfa59f44d8f65bfdda132bff61d8f8f29af1d6/server/middleware.go
