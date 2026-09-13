# [C] Cal.com has an Authentication Bypass via Unvalidated Email in Custom JWT Callback

## Summary
Severity: Critical
Advisory: CVE-2026-23478
Aliases: GHSA-7hg4-x4pr-3hrg
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:L)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2026-23478
Type: osv

## Details
Cal.com is open-source scheduling software. From 3.1.6 to before 6.0.7, there is a vulnerability in a custom NextAuth JWT callback that allows attackers to gain full authenticated access to any user's account by supplying a target email address via session.update(). This vulnerability is fixed in 6.0.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23478.json
- https://github.com/calcom/cal.com/security/advisories/GHSA-7hg4-x4pr-3hrg
- https://nvd.nist.gov/vuln/detail/CVE-2026-23478
