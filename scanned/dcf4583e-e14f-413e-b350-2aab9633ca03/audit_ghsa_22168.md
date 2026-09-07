# [H] RCE vulnerability in SCM Filter Jervis Plugin

## Summary
Severity: High
Advisory: GHSA-4hhq-j3xw-wj89
CVE: CVE-2020-2189
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4hhq-j3xw-wj89
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:scm-filter-jervis` — affected >=0 <0.3

## Details
SCM Filter Jervis Plugin 0.2.1 and earlier does not configure its YAML parser to prevent the instantiation of arbitrary types. This results in a remote code execution (RCE) vulnerability exploitable by users able to configure jobs with the filter, or control the contents of a previously configured job’s SCM repository.

SCM Filter Jervis Plugin 0.3 configures its YAML parser to only instantiate safe types.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2189
- https://github.com/jenkinsci/scm-filter-jervis-plugin/commit/a36e8bdef3a2a84737b64a898da4106793997273
- https://github.com/jenkinsci/scm-filter-jervis-plugin
- https://jenkins.io/security/advisory/2020-05-06/#SECURITY-1826
- http://www.openwall.com/lists/oss-security/2020/05/06/3
