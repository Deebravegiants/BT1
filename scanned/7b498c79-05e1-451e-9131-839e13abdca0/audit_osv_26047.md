# [M] CVE-2023-50019

## Summary
Severity: Medium
Advisory: CVE-2023-50019
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-02
Source: https://osv.dev/vulnerability/CVE-2023-50019
Type: osv

## Details
An issue was discovered in open5gs v2.6.6. InitialUEMessage, Registration request sent at a specific time can crash AMF due to incorrect error handling of Nudm_UECM_Registration response.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50019.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-50019
- https://github.com/open5gs/open5gs/issues/2733
- https://github.com/open5gs/open5gs/commit/7278714133422cee46c32c7523f81ec2cecad9e2
