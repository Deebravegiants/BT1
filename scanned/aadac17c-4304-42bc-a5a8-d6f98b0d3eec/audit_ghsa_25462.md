# [M] Jenkins Upload to pgyer Plugin stores credentials in plain text 

## Summary
Severity: Medium
Advisory: GHSA-wchh-wvpx-pf47
CVE: CVE-2019-1003089
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wchh-wvpx-pf47
Type: github-advisory

## Affected
- Maven: `ren.helloworld:upload-pgyer` — affected >=0 <1.33

## Details
Jenkins Upload to pgyer Plugin stores credentials unencrypted in job config.xml files on the Jenkins master where they can be viewed by users with Extended Read permission, or access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003089
- https://github.com/jenkinsci/upload-pgyer-plugin/commit/af4e89754c31a0d71b98d3f360088e8dae36a313
- https://github.com/jenkinsci/upload-pgyer-plugin
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-1044
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
