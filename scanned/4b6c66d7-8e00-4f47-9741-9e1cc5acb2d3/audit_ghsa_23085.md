# [M] Skytap Cloud CI Plugin stored credentials in plain text 

## Summary
Severity: Medium
Advisory: GHSA-vp26-4hj6-jrvx
CVE: CVE-2019-10366
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vp26-4hj6-jrvx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:skytap` — affected >=0 <2.07

## Details
Jenkins Skytap Cloud CI Plugin 2.06 and earlier stored credentials unencrypted in job config.xml files on the Jenkins master where they could be viewed by users with Extended Read permission, or access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10366
- https://github.com/jenkinsci/skytap-cloud-plugin/commit/167986a84d1d15b525eaf0232b1c1a7c47aef670
- https://github.com/jenkinsci/skytap-cloud-plugin
- https://jenkins.io/security/advisory/2019-07-31/#SECURITY-1429
- https://www.zerodayinitiative.com/advisories/ZDI-19-833
- http://www.openwall.com/lists/oss-security/2019/07/31/1
