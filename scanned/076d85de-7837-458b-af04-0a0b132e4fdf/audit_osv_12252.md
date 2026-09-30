# [M] CVE-2018-11084

## Summary
Severity: Medium
Advisory: CVE-2018-11084
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-09-18
Source: https://osv.dev/vulnerability/CVE-2018-11084
Type: osv

## Details
Cloud Foundry Garden-runC release, versions prior to 1.16.1, prevents deletion of some app environments based on file attributes. A remote authenticated malicious user may create and delete apps with crafted file attributes to cause a denial of service for new app instances or scaling up of existing apps.

## References
- https://www.cloudfoundry.org/blog/cve-2018-11084/
