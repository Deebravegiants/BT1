# [M] CVE-2020-2127

## Summary
Severity: Medium
Advisory: CVE-2020-2127
Aliases: GHSA-2j3r-x6xc-qqqj
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-02-12
Source: https://osv.dev/vulnerability/CVE-2020-2127
Type: osv

## Details
Jenkins BMC Release Package and Deployment Plugin 1.1 and earlier stores credentials unencrypted in its global configuration file on the Jenkins master where they can be viewed by users with access to the master file system.

## References
- http://www.openwall.com/lists/oss-security/2020/02/12/3
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-1547
