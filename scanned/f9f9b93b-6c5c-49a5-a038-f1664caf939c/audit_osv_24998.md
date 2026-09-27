# [M] CVE-2023-29415

## Summary
Severity: Medium
Advisory: CVE-2023-29415
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-04-06
Source: https://osv.dev/vulnerability/CVE-2023-29415
Type: osv

## Details
An issue was discovered in libbzip3.a in bzip3 before 1.3.0. A denial of service (process hang) can occur with a crafted archive because bzip3 does not follow the required procedure for interacting with libsais.

## References
- https://github.com/kspalaiologos/bzip3/compare/1.2.3...1.3.0
- https://security-tracker.debian.org/tracker/CVE-2023-29415
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29415.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4JLSE25SV7K2NB6FTFT4UHJOJUHBHYHY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NA7S7HDUAINOTCSWQZ5LIW756DYY22V2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NMLFV2FJK3CM7NJLVPZI5RUAFQZICPWW/
- https://nvd.nist.gov/vuln/detail/CVE-2023-29415
- https://github.com/kspalaiologos/bzip3/issues/95
