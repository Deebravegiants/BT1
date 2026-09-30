# [M] CVE-2021-21661

## Summary
Severity: Medium
Advisory: CVE-2021-21661
Aliases: GHSA-xrg9-wwrq-xmx9
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-06-10
Source: https://osv.dev/vulnerability/CVE-2021-21661
Type: osv

## Details
Jenkins Kubernetes CLI Plugin 1.10.0 and earlier does not perform permission checks in several HTTP endpoints, allowing attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins.

## References
- http://www.openwall.com/lists/oss-security/2021/06/10/14
- https://www.jenkins.io/security/advisory/2021-06-10/#SECURITY-2370
