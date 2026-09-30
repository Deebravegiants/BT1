# [H] Return of Pointer Value Outside of Expected Rang in Jenkins Script Security Plugin

## Summary
Severity: High
Advisory: GHSA-x25x-j4w4-7m59
CVE: CVE-2019-10356
CWE: CWE-466
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x25x-j4w4-7m59
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1.62

## Details
A sandbox bypass vulnerability in Jenkins Script Security Plugin 1.61 and earlier related to the handling of method pointer expressions allowed attackers to execute arbitrary code in sandboxed scripts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10356
- https://access.redhat.com/errata/RHSA-2019:2594
- https://access.redhat.com/errata/RHSA-2019:2651
- https://access.redhat.com/errata/RHSA-2019:2662
- https://jenkins.io/security/advisory/2019-07-31/#SECURITY-1465%20(2)
- http://www.openwall.com/lists/oss-security/2019/07/31/1
