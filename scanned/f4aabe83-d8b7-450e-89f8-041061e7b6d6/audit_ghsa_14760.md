# [H] GoPhish sends cleartext passwords

## Summary
Severity: High
Advisory: GHSA-rv83-h68q-c4wq
CVE: CVE-2024-55196
CWE: CWE-312
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-19
Source: https://github.com/advisories/GHSA-rv83-h68q-c4wq
Type: github-advisory

## Affected
- Go: `github.com/gophish/gophish` — affected >=0

## Details
Insufficiently Protected Credentials in the Mail Server Configuration in GoPhish v0.12.1 allows an attacker to access cleartext passwords for the configured IMAP and SMTP servers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-55196
- https://github.com/gophish/gophish
- https://github.com/hexkaster/SecurityResearch/blob/main/CVE-2024-55196.md
