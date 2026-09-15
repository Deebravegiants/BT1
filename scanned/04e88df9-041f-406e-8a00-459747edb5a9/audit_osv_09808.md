# [H] CVE-2017-11553

## Summary
Severity: High
Advisory: CVE-2017-11553
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-23
Source: https://osv.dev/vulnerability/CVE-2017-11553
Type: osv

## Details
There is an illegal address access in the extend_alias_table function in localealias.c of Exiv2 0.26. A crafted input will lead to remote denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1471772
