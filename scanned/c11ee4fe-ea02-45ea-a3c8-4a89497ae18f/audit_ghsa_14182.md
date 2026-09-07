# [H] Jenkins Pipeline Aggregator View Plugin vulnerable to Cross-site Scripting

## Summary
Severity: High
Advisory: GHSA-v27q-87jf-j9cr
CVE: CVE-2023-28670
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-02
Source: https://github.com/advisories/GHSA-v27q-87jf-j9cr
Type: github-advisory

## Affected
- Maven: `com.paul8620.jenkins.plugins:pipeline-aggregator-view` — affected >=0 <1.14

## Details
Jenkins Pipeline Aggregator View Plugin 1.13 and earlier does not escape a variable representing the current view's URL in inline JavaScript, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by authenticated attackers with Overall/Read permission. Version 1.14 obtains the current URL in a way not susceptible to XSS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28670
- https://github.com/jenkinsci/pipeline-aggregator-view-plugin
- https://www.jenkins.io/security/advisory/2023-03-21/#SECURITY-2885
