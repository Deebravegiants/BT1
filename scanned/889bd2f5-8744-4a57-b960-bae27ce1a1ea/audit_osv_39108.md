# [H] Vaultwarden: Brute-force protection bypass vulnerability

## Summary
Severity: High
Advisory: CVE-2026-43914
Aliases: GHSA-c5rv-q295-7w4g
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-43914
Type: osv

## Details
Vaultwarden is a Bitwarden-compatible server written in Rust. Prior to 1.35.4, there is a security vulnerability in Vaultwarden that allows bypassing the login brute-force protection if email 2fa is enabled. If email 2fa is enabled, the unprotected 2fa-function send_email_login (email.rs, api endpoint /api/two-factor/send-email-login) also acts as an oracle determining whether a username-password combination is correct. An attacker can abuse that endpoint to brute-force passwords without rate-limiting. This works even for users who don't have email 2fa configured. This vulnerability is fixed in 1.35.4.

## References
- https://github.com/dani-garcia/vaultwarden/releases/tag/1.35.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43914.json
- https://github.com/dani-garcia/vaultwarden/security/advisories/GHSA-c5rv-q295-7w4g
- https://nvd.nist.gov/vuln/detail/CVE-2026-43914
- https://github.com/dani-garcia/vaultwarden/pull/6867
