# [H] Spring Cloud Config Profile Substitution Can Allow Unintended Access To Files And Enable SSRF Attacks

## Summary
Severity: High
Advisory: CVE-2026-22739
Aliases: GHSA-3qwq-q9vm-5j42
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/CVE-2026-22739
Type: osv

## Details
Vulnerability in Spring Cloud when substituting the profile parameter from a request made to the Spring Cloud Config Server configured to the native file system as a backend, because it was possible to access files outside of the configured search directories.This issue affects Spring Cloud: from 3.1.X before 3.1.13, from 4.1.X before 4.1.9, from 4.2.X before 4.2.3, from 4.3.X before 4.3.2, from 5.0.X before 5.0.2.

## References
- https://spring.io/security/cve-2026-22739
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22739.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22739
