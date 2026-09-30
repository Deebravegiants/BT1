# [M] Stack overflow in Jsonxx

## Summary
Severity: Medium
Advisory: CVE-2022-23460
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-19
Source: https://osv.dev/vulnerability/CVE-2022-23460
Type: osv

## Details
Jsonxx or Json++ is a JSON parser, writer and reader written in C++. In affected versions of jsonxx json parsing may lead to stack exhaustion in an address sanitized (ASAN) build. This issue may lead to Denial of Service if the program using the jsonxx library crashes. This issue exists on the current commit of the jsonxx project and the project itself has been archived. Updates are not expected. Users are advised to find a replacement.

## References
- https://securitylab.github.com/advisories/GHSL-2022-049_Jsonxx
