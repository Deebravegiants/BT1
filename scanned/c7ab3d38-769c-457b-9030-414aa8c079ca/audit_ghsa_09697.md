# [C] Jenkins GitHub Plugin has an XSS vulnerability

## Summary
Severity: Critical
Advisory: GHSA-w22p-4x9f-486v
CVE: CVE-2026-42523
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-w22p-4x9f-486v
Type: github-advisory

## Affected
- Maven: `com.coravy.hudson.plugins.github:github` — affected >=0 <1.46.0.1

## Details
In Jenkins GitHub Plugin versions 1.46.0 and earlier, the JavaScript that validates the "GitHub hook trigger for GITScm polling" feature improperly processes the current job URL.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by non-anonymous attackers with Overall/Read permission.

GitHub Plugin 1.46.0.1 no longer processes the current job URL as part of JavaScript implementing validation of the feature "GitHub hook trigger for GITScm polling".

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42523
- https://github.com/jenkinsci/github-plugin
- https://www.jenkins.io/security/advisory/2026-04-29/#SECURITY-3704
