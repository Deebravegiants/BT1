# [M] Password stored in plain text by Jenkins Proxmox Plugin

## Summary
Severity: Medium
Advisory: GHSA-w97x-j6rg-55v5
CVE: CVE-2022-28141
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-w97x-j6rg-55v5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:proxmox` — affected >=0 <0.6.0

## Details
Jenkins Proxmox Plugin 0.5.0 and earlier stores the Proxmox Datacenter password unencrypted in the global config.xml file on the Jenkins controller where it can be viewed by users with access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28141
- https://github.com/jenkinsci/proxmox-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-2079
- http://www.openwall.com/lists/oss-security/2022/03/29/1
