# [M] CSRF vulnerability in Jenkins promoted builds Plugin

## Summary
Severity: Medium
Advisory: GHSA-5cxw-8v65-76vf
CVE: CVE-2021-21641
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5cxw-8v65-76vf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:promoted-builds` — affected >=0 <3.9.1

## Details
Jenkins promoted builds Plugin 3.9 and earlier does not require POST requests for HTTP endpoints implementing promotion (regular, forced, and re-execute), resulting in cross-site request forgery (CSRF) vulnerabilities.

These vulnerabilities allow attackers to promote builds.

Jenkins promoted builds Plugin 3.9.1 requires POST requests for the affected HTTP endpoints.

A security hardening since Jenkins 2.287 and LTS 2.277.2 prevents exploitation of this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21641
- https://github.com/jenkinsci/promoted-builds-plugin/commit/46086a74891d620042c3d28a19cba3510c5dbf6a
- https://github.com/jenkinsci/promoted-builds-plugin
- https://www.jenkins.io/security/advisory/2021-04-07/#SECURITY-2293
- http://www.openwall.com/lists/oss-security/2021/04/07/2
