# [H] CVE-2019-3806

## Summary
Severity: High
Advisory: CVE-2019-3806
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-29
Source: https://osv.dev/vulnerability/CVE-2019-3806
Type: osv

## Details
An issue has been found in PowerDNS Recursor versions after 4.1.3 before 4.1.9 where Lua hooks are not properly applied to queries received over TCP in some specific combination of settings, possibly bypassing security policies enforced using Lua.

## References
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-2019-01.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3806
