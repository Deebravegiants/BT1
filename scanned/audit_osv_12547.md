# [M] CVE-2018-1277

## Summary
Severity: Medium
Advisory: CVE-2018-1277
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-30
Source: https://osv.dev/vulnerability/CVE-2018-1277
Type: osv

## Details
Cloud Foundry Garden-runC, versions prior to 1.13.0, does not correctly enforce disc quotas for Docker image layers. A remote authenticated user may push an app with a malicious Docker image that will consume more space on a Diego cell than allocated in their quota, potentially causing a DoS against the cell.

## References
- https://www.cloudfoundry.org/blog/cve-2018-1277/
