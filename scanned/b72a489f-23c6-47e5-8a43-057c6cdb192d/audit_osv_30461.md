# [H] CVE-2024-52946

## Summary
Severity: High
Advisory: CVE-2024-52946
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-18
Source: https://osv.dev/vulnerability/CVE-2024-52946
Type: osv

## Details
An issue was discovered in LemonLDAP::NG before 2.20.1. An Improper Check during session refresh allows an authenticated user to raise their authentication level if the admin configured an "Adaptative authentication rule" with an increment instead of an absolute value.

## References
- https://lists.debian.org/debian-lts-announce/2024/11/msg00037.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52946.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-52946
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/issues/3255
