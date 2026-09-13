# [H] CVE-2019-10287

## Summary
Severity: High
Advisory: CVE-2019-10287
Aliases: GHSA-c7p6-x2p3-3wph
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-04
Source: https://osv.dev/vulnerability/CVE-2019-10287
Type: osv

## Details
Jenkins youtrack-plugin Plugin 0.7.1 and older stored credentials unencrypted in its global configuration file on the Jenkins master where they could be viewed by users with access to the master file system.

## References
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-963
