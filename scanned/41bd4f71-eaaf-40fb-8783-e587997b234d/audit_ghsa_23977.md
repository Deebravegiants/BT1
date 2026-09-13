# [H] RCE vulnerability in Jenkins Code Coverage API Plugin

## Summary
Severity: High
Advisory: GHSA-58pr-hprx-7hg6
CVE: CVE-2021-21677
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-58pr-hprx-7hg6
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:code-coverage-api` — affected >=0 <1.4.1

## Details
Jenkins Code Coverage API Plugin 1.4.0 and earlier does not apply [JEP-200 deserialization protection](https://github.com/jenkinsci/jep/tree/master/jep/200) to Java objects it deserializes from disk.

This results in a remote code execution (RCE) vulnerability exploitable by attackers able to control agent processes.

Jenkins Code Coverage API Plugin 1.4.1 configures its Java object deserialization to only deserialize safe types.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21677
- https://github.com/jenkinsci/code-coverage-api-plugin/commit/a5b3c18cff2a0b494c55fa73b05fc935b50530be
- https://github.com/jenkinsci/code-coverage-api-plugin
- https://www.jenkins.io/security/advisory/2021-08-31/#SECURITY-2376
- http://www.openwall.com/lists/oss-security/2021/08/31/1
