# [M] CVE-2016-8219

## Summary
Severity: Medium
Advisory: CVE-2016-8219
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-13
Source: https://osv.dev/vulnerability/CVE-2016-8219
Type: osv

## Details
An issue was discovered in Cloud Foundry Foundation cf-release versions prior to 250 and CAPI-release versions prior to 1.12.0. A user with the SpaceAuditor role is over-privileged with the ability to restage applications. This could cause application downtime if the restage fails.

## References
- https://www.cloudfoundry.org/cve-2016-8219/
