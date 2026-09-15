# [H] CVE-2022-3767

## Summary
Severity: High
Advisory: CVE-2022-3767
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2023-03-09
Source: https://osv.dev/vulnerability/CVE-2022-3767
Type: osv

## Details
Missing validation in DAST analyzer affecting all versions from 1.11.0 prior to 3.0.32, allows custom request headers to be sent with every request, regardless of the host.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3767.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3767.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3767
- https://gitlab.com/gitlab-org/gitlab/-/issues/377473
