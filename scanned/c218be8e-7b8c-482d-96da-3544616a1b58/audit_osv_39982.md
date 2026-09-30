# [H] Forem vulnerable to bypass of email address domain restrictions

## Summary
Severity: High
Advisory: CVE-2026-48780
Aliases: GHSA-3g4h-9h37-mpx6
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-48780
Type: osv

## Details
Forem is open source software for building communities. Prior to commit a2ab6d4, a maliciously crafted email address could allow an attacker to bypass domain allowlist or denylist restrictions and gain access to invite-only forem deployments. The issue is patched as of `a2ab6d4`. As a workaround, some SMTP servers and email delivery providers may drop or refuse to send maliciously crafted email addresses.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48780.json
- https://github.com/forem/forem/security/advisories/GHSA-3g4h-9h37-mpx6
- https://nvd.nist.gov/vuln/detail/CVE-2026-48780
- https://github.com/forem/forem/commit/a2ab6d409d2676eb0711ecbd737192043125b437
