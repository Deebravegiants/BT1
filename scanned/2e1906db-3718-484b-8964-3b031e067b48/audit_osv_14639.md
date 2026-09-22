# [M] CVE-2019-10385

## Summary
Severity: Medium
Advisory: CVE-2019-10385
Aliases: GHSA-xj63-95xc-jc4v
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-08-07
Source: https://osv.dev/vulnerability/CVE-2019-10385
Type: osv

## Details
Jenkins eggPlant Plugin 2.2 and earlier stores credentials unencrypted in job config.xml files on the Jenkins master where they can be viewed by users with Extended Read permission, or access to the master file system.

## References
- http://www.openwall.com/lists/oss-security/2019/08/07/1
- https://jenkins.io/security/advisory/2019-08-07/#SECURITY-1430
- https://www.zerodayinitiative.com/advisories/ZDI-19-834/
