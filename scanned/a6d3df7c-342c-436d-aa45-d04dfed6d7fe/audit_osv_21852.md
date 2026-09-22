# [H] CVE-2022-0270

## Summary
Severity: High
Advisory: CVE-2022-0270
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-25
Source: https://osv.dev/vulnerability/CVE-2022-0270
Type: osv

## Details
Prior to v0.6.1, bored-agent failed to sanitize incoming kubernetes impersonation headers allowing a user to override assigned user name and groups.

## References
- https://github.com/Mirantis/security/blob/main/advisories/0004.md
