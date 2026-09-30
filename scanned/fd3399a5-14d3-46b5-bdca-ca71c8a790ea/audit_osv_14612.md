# [H] CVE-2019-10303

## Summary
Severity: High
Advisory: CVE-2019-10303
Aliases: GHSA-rfc8-wrrf-wp3w
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-18
Source: https://osv.dev/vulnerability/CVE-2019-10303
Type: osv

## Details
Jenkins Azure PublisherSettings Credentials Plugin 1.2 and earlier stored credentials unencrypted in the credentials.xml file on the Jenkins master where they could be viewed by users with access to the master file system.

## References
- http://www.securityfocus.com/bid/108045
- https://jenkins.io/security/advisory/2019-04-17/#SECURITY-844
