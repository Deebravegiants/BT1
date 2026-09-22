# [H] CVE-2019-20393

## Summary
Severity: High
Advisory: CVE-2019-20393
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-01-22
Source: https://osv.dev/vulnerability/CVE-2019-20393
Type: osv

## Details
A double-free is present in libyang before v1.0-r1 in the function yyparse() when an empty description is used. Applications that use libyang to parse untrusted input yang files may be vulnerable to this flaw, which would cause a crash or potentially code execution.

## References
- https://lists.debian.org/debian-lts-announce/2023/09/msg00019.html
- https://github.com/CESNET/libyang/compare/v0.16-r3...v1.0-r1
- https://bugzilla.redhat.com/show_bug.cgi?id=1793930
- https://github.com/CESNET/libyang/commit/d9feacc4a590d35dbc1af21caf9080008b4450ed
- https://github.com/CESNET/libyang/issues/742
