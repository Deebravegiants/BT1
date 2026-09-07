# [H] Stored XSS vulnerability in Jenkins Checkmarx Plugin

## Summary
Severity: High
Advisory: GHSA-p86x-75j8-w4xh
CVE: CVE-2022-46684
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-12
Source: https://github.com/advisories/GHSA-p86x-75j8-w4xh
Type: github-advisory

## Affected
- Maven: `com.checkmarx.jenkins:checkmarx` — affected >=0 <2022.4.3

## Details
heckmarx Plugin processes Checkmarx service API responses and generates HTML reports from them for rendering on the Jenkins UI.

Checkmarx Plugin 2022.3.3 and earlier does not escape values returned from the Checkmarx service API before inserting them into HTML reports. This results in a stored cross-site scripting (XSS) vulnerability.

While Jenkins users without Overall/Administer permission are not allowed to configure the URL to the Checkmarx service, this could still be exploited via man-in-the-middle attacks.

Checkmarx Plugin 2022.4.3 escapes values returned from the Checkmarx service API before inserting them into HTML reports.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-46684
- https://github.com/jenkinsci/checkmarx-plugin
- https://www.jenkins.io/security/advisory/2022-12-07/#SECURITY-2869
