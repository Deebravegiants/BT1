# [M] CVE-2020-2126

## Summary
Severity: Medium
Advisory: CVE-2020-2126
Aliases: GHSA-8g6v-g8qc-5w7j
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-02-12
Source: https://osv.dev/vulnerability/CVE-2020-2126
Type: osv

## Details
Jenkins DigitalOcean Plugin 1.1 and earlier stores a token unencrypted in the global config.xml file on the Jenkins master where it can be viewed by users with access to the master file system.

## References
- http://www.openwall.com/lists/oss-security/2020/02/12/3
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-1559
