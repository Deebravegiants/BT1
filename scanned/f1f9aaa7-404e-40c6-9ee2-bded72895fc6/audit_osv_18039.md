# [M] CVE-2020-2319

## Summary
Severity: Medium
Advisory: CVE-2020-2319
Aliases: GHSA-cg4h-cfjp-h3x2
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-11-04
Source: https://osv.dev/vulnerability/CVE-2020-2319
Type: osv

## Details
Jenkins VMware Lab Manager Slaves Plugin 0.2.8 and earlier stores a password unencrypted in the global config.xml file on the Jenkins controller where it can be viewed by users with access to the Jenkins controller file system.

## References
- https://www.jenkins.io/security/advisory/2020-11-04/#SECURITY-2084
