# [M] CVE-2022-37186

## Summary
Severity: Medium
Advisory: CVE-2022-37186
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-04-16
Source: https://osv.dev/vulnerability/CVE-2022-37186
Type: osv

## Details
In LemonLDAP::NG before 2.0.15. some sessions are not deleted when they are supposed to be deleted according to the timeoutActivity setting. This can occur when there are at least two servers, and a session is manually removed before the time at which it would have been removed automatically.

## References
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/releases/v2.0.15
- https://lists.debian.org/debian-lts-announce/2023/01/msg00027.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/37xxx/CVE-2022-37186.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-37186
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/issues/2758
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/commit/59c781b393947663ad3bf26bad0581413dd6fae4
