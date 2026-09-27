# [M] CVE-2020-2131

## Summary
Severity: Medium
Advisory: CVE-2020-2131
Aliases: GHSA-qj7p-9hgf-x8j7
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-02-12
Source: https://osv.dev/vulnerability/CVE-2020-2131
Type: osv

## Details
Jenkins Harvest SCM Plugin 0.5.1 and earlier stores passwords unencrypted in job config.xml files on the Jenkins master where they can be viewed by users with Extended Read permission, or access to the master file system.

## References
- http://www.openwall.com/lists/oss-security/2020/02/12/3
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-1553
