# [H] Stored XSS vulnerability in android-lint Plugin

## Summary
Severity: High
Advisory: GHSA-28x9-hc4p-9vh2
CVE: CVE-2020-2262
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-28x9-hc4p-9vh2
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:android-lint` — affected >=0

## Details
Jenkins Android Lint Plugin 2.6 and earlier does not escape the annotation message in tooltips, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to provide report files to the plugin's post-build step.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2262
- https://github.com/jenkinsci/android-lint-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1908
- http://www.openwall.com/lists/oss-security/2020/09/16/3
