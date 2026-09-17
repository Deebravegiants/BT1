# [H] Double free or Use after Free in Value class of Jsonxx

## Summary
Severity: High
Advisory: CVE-2022-23459
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-19
Source: https://osv.dev/vulnerability/CVE-2022-23459
Type: osv

## Details
Jsonxx or Json++ is a JSON parser, writer and reader written in C++. In affected versions of jsonxx use of the Value class may lead to memory corruption via a double free or via a use after free. The value class has a default assignment operator which may be used with pointer types which may point to alterable data where the pointer itself is not updated. This issue exists on the current commit of the jsonxx project. The project itself has been archived and updates are not expected. Users are advised to find a replacement.

## References
- https://securitylab.github.com/advisories/GHSL-2022-048_Jsonxx
