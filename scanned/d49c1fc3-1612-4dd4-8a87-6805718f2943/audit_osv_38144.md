# [H] hoppscotch: Improper loopback redirect_uri validation in device-login flow

## Summary
Severity: High
Advisory: CVE-2026-34931
Aliases: GHSA-7fg7-wx5q-6m3v
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-34931
Type: osv

## Details
hoppscotch is an open source API development ecosystem. Prior to version 2026.3.0, there is an open redirect vulnerability that leads to token exfiltration. With these tokens, the attacker can sign in as the victim to takeover their account. This issue has been patched in version 2026.3.0.

## References
- https://github.com/hoppscotch/hoppscotch/releases/tag/2026.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34931.json
- https://github.com/hoppscotch/hoppscotch/security/advisories/GHSA-7fg7-wx5q-6m3v
- https://nvd.nist.gov/vuln/detail/CVE-2026-34931
