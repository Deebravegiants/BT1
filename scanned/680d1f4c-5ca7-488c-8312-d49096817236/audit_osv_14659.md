# [H] CVE-2019-10461

## Summary
Severity: High
Advisory: CVE-2019-10461
Aliases: GHSA-6xw9-qq9h-cr68
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-23
Source: https://osv.dev/vulnerability/CVE-2019-10461
Type: osv

## Details
Jenkins Dynatrace Application Monitoring Plugin 2.1.3 and earlier stored credentials unencrypted in its global configuration file on the Jenkins master where they could be viewed by users with access to the master file system.

## References
- http://www.openwall.com/lists/oss-security/2019/10/23/2
- https://jenkins.io/security/advisory/2019-10-23/#SECURITY-1477
