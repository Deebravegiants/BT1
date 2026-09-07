# [M] Jenkins NodeJS Plugin improper credential masking vulnerability

## Summary
Severity: Medium
Advisory: GHSA-36fg-whr2-g999
CVE: CVE-2023-40340
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-08-16
Source: https://github.com/advisories/GHSA-36fg-whr2-g999
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:nodejs` — affected >=0 <1.6.1

## Details
Jenkins NodeJS Plugin integrates with Config File Provider Plugin to specify custom NPM settings, including credentials for authentication, in a Npm config file.

NodeJS Plugin 1.6.0 and earlier does not properly mask (i.e., replace with asterisks) credentials specified in the Npm config file in Pipeline build logs.

NodeJS Plugin 1.6.1 masks credentials specified in the Npm config file in Pipeline build logs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40340
- https://github.com/jenkinsci/nodejs-plugin/commit/a2198feb53765f0b1f063b1827e90473a60a25a0
- https://www.jenkins.io/security/advisory/2023-08-16/#SECURITY-3196
- http://www.openwall.com/lists/oss-security/2023/08/16/3
