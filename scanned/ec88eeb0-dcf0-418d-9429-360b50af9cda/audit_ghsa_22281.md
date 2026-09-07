# [H] Stored XSS vulnerability in computer-queue-plugin Plugin

## Summary
Severity: High
Advisory: GHSA-qg66-xv7v-m834
CVE: CVE-2020-2259
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qg66-xv7v-m834
Type: github-advisory

## Affected
- Maven: `jenkins.ci.plugins.computerqueue:computer-queue-plugin` — affected >=0 <1.6

## Details
computer-queue-plugin Plugin 1.5 and earlier does not escape the agent name in tooltips.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Agent/Configure permission.

computer-queue-plugin Plugin 1.6 escapes the agent name in tooltips.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2259
- https://github.com/jenkinsci/computer-queue-plugin/commit/38776c0716470038d922829f675ab278a079acfb
- https://github.com/jenkinsci/computer-queue-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1912
- http://www.openwall.com/lists/oss-security/2020/09/16/3
