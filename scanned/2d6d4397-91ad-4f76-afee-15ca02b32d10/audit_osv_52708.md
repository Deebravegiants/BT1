# [H] CVE-2022-0497

## Summary
Severity: High
Advisory: CVE-2022-0497
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2022-08-29
Source: https://osv.dev/vulnerability/CVE-2022-0497
Type: osv

## Details
A vulnerbiility was found in Openscad, where a .scad file with no trailing newline could cause an out-of-bounds read during parsing of annotations.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2050699
- https://github.com/openscad/openscad/issues/4043
- https://github.com/openscad/openscad/pull/4044
