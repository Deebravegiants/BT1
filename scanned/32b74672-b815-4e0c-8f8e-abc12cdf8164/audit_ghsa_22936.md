# [M] CSRF vulnerability in Jenkins Lockable Resources Plugin

## Summary
Severity: Medium
Advisory: GHSA-rvww-w62m-hch8
CVE: CVE-2020-2281
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rvww-w62m-hch8
Type: github-advisory

## Affected
- Maven: `org.6wind.jenkins:lockable-resources` — affected >=0 <2.9

## Details
Lockable Resources Plugin 2.8 and earlier does not require POST requests for several HTTP endpoints, resulting in a cross-site request forgery (CSRF) vulnerability. This vulnerability allows attackers to reserve, unreserve, unlock, and reset resources. Lockable Resources Plugin 2.9 requires POST requests for the affected HTTP endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2281
- https://github.com/jenkinsci/lockable-resources-plugin/commit/50ab82498f792775a761e6f4937607b240ecde67
- https://github.com/jenkinsci/lockable-resources-plugin
- https://www.jenkins.io/security/advisory/2020-09-23/#SECURITY-1958
- http://www.openwall.com/lists/oss-security/2020/09/23/1
