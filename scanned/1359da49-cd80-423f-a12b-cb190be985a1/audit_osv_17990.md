# [M] CVE-2020-2239

## Summary
Severity: Medium
Advisory: CVE-2020-2239
Aliases: GHSA-wphq-j78p-fhgp
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-09-01
Source: https://osv.dev/vulnerability/CVE-2020-2239
Type: osv

## Details
Jenkins Parameterized Remote Trigger Plugin 3.1.3 and earlier stores a secret unencrypted in its global configuration file on the Jenkins controller where it can be viewed by attackers with access to the Jenkins controller file system.

## References
- http://www.openwall.com/lists/oss-security/2020/09/01/3
- https://jenkins.io/security/advisory/2020-09-01/#SECURITY-1625
