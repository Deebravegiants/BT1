# [C] CVE-2018-7485

## Summary
Severity: Critical
Advisory: CVE-2018-7485
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-26
Source: https://osv.dev/vulnerability/CVE-2018-7485
Type: osv

## Details
The SQLWriteFileDSN function in odbcinst/SQLWriteFileDSN.c in unixODBC 2.3.5 has strncpy arguments in the wrong order, which allows attackers to cause a denial of service or possibly have unspecified other impact.

## References
- http://www.securityfocus.com/bid/103193
- https://access.redhat.com/errata/RHSA-2019:2336
- https://github.com/lurcher/unixODBC/commit/45ef78e037f578b15fc58938a3a3251655e71d6f#diff-d52750c7ba4e594410438569d8e2963aL24
