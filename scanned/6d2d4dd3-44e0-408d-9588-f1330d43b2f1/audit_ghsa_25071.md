# [M] Exposure of sensitive information vulnerability

## Summary
Severity: Medium
Advisory: GHSA-68qx-whxm-h4c4
CVE: CVE-2018-1999041
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-68qx-whxm-h4c4
Type: github-advisory

## Affected
- Maven: `com.tinfoilsecurity.plugins:tinfoil-scan` — affected >=0 <2.0

## Details
An exposure of sensitive information vulnerability exists in Jenkins Tinfoil Security Plugin 1.6.1 and earlier in TinfoilScanRecorder.java that allows attackers with file system access to the Jenkins master to obtain the API secret key stored in this plugin's configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999041
- https://github.com/jenkinsci/tinfoil-scan-plugin/commit/26b39449fd75213973a509accde5b3938dbd1f91
- https://github.com/jenkinsci/tinfoil-scan-plugin
- https://jenkins.io/security/advisory/2018-07-30/#SECURITY-840
