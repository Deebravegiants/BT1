# [H] Jenkins Gatling Plugin Vulnerable to Cross-Site Scripting (XSS)

## Summary
Severity: High
Advisory: GHSA-gw97-cqwg-xmh4
CVE: CVE-2025-5806
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-06
Source: https://github.com/advisories/GHSA-gw97-cqwg-xmh4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:gatling` — affected 136.vb

## Details
Jenkins Gatling Plugin 136.vb_9009b_3d33a_e serves Gatling reports in a manner that bypasses the Content-Security-Policy protection introduced in Jenkins 1.641 and 1.625, resulting in a cross-site scripting (XSS) vulnerability exploitable by users able to change report content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-5806
- https://github.com/jenkinsci/gatling-plugin/pull/27
- https://github.com/jenkinsci/gatling-plugin/commit/141bd3a811ab641bf618ec588b615cf87469b222
- https://github.com/jenkinsci/gatling-plugin
- https://github.com/jenkinsci/gatling-plugin/releases/tag/136.vb_9009b_3d33a_e
- https://www.jenkins.io/security/advisory/2025-06-06/#SECURITY-3588
- http://www.openwall.com/lists/oss-security/2025/06/06/8
