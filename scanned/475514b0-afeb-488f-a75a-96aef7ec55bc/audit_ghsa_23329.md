# [M] Missing SSH host key validation in Mac Plugin

## Summary
Severity: Medium
Advisory: GHSA-rv9g-67f7-grq7
CVE: CVE-2020-2146
CWE: CWE-347
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rv9g-67f7-grq7
Type: github-advisory

## Affected
- Maven: `fr.edf.jenkins.plugins:mac` — affected >=0 <1.2.0

## Details
Mac Plugin 1.1.0 and earlier does not use SSH host key validation when connecting to Mac Cloud host launched by the plugin. This lack of validation could be abused using a man-in-the-middle attack to intercept these connections to build agents.

Mac Plugin 1.2.0 validates SSH host keys when connecting to agents.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2146
- https://github.com/jenkinsci/mac-plugin/commit/ba1a8206c7ef990d37498e5abdf210990ef046b5
- https://github.com/jenkinsci/mac-plugin
- https://jenkins.io/security/advisory/2020-03-09/#SECURITY-1692
- http://www.openwall.com/lists/oss-security/2020/03/09/1
