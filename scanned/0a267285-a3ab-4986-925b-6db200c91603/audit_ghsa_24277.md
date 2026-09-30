# [M] Project Inheritance Plugin showed secret environment variables defined in Mask Passwords Plugin 

## Summary
Severity: Medium
Advisory: GHSA-xj4w-r6gr-x5qm
CVE: CVE-2019-10407
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xj4w-r6gr-x5qm
Type: github-advisory

## Affected
- Maven: `hudson.plugins:project-inheritance` — affected >=0 <19.08.02

## Details
Jenkins Project Inheritance Plugin 19.08.02 and earlier displayed a list of environment variables passed to a build without masking sensitive variables contributed by the Mask Passwords Plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10407
- https://jenkins.io/security/advisory/2019-09-25/#SECURITY-351
- http://www.openwall.com/lists/oss-security/2019/09/25/3
