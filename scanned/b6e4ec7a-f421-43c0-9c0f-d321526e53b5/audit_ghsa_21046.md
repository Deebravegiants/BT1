# [H] Stored XSS vulnerability in Jenkins Dynamic Extended Choice Parameter plugin

## Summary
Severity: High
Advisory: GHSA-jvvx-hmmr-rhgg
CVE: CVE-2022-36902
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-jvvx-hmmr-rhgg
Type: github-advisory

## Affected
- Maven: `com.moded.extendedchoiceparameter:dynamic_extended_choice_parameter` — affected >=0

## Details
Jenkins Dynamic Extended Choice Parameter Plugin 1.0.1 and earlier does not escape several fields of Moded Extended Choice parameters, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36902
- https://github.com/jenkinsci/dynamic-extended-choice-parameter-plugin
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2682
- http://www.openwall.com/lists/oss-security/2022/07/27/1
