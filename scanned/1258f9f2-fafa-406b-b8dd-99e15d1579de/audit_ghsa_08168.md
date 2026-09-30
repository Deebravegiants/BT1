# [C] survey-pdf Upgraded jsPDF Version Due to Security Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-h3q6-jfrg-3x6q
CVE: CVE-2026-25630
CWE: CWE-35, CWE-73
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-h3q6-jfrg-3x6q
Type: github-advisory

## Affected
- npm: `survey-pdf` — affected >=0 <1.12.59
- npm: `survey-pdf` — affected >=2.0.0 <2.5.5

## Details
The following security vulnerability was identified in jsPDF versions <=3.0.4: [Local File Inclusion/Path Traversal](https://github.com/parallax/jsPDF/security/advisories/GHSA-f8cm-6447-x5h2).

### Impact

Since SurveyJS PDF Generator depends on jsPDF, any project using `survey-pdf` v1.12.58 and lower or v2.5.4 and lower could be exposed to this vulnerability.

### Solution

SurveyJS PDF Generator has upgraded jsPDF to version >= 4.0.0 and included the fix in the following `survey-pdf` releases:

* [v1.12.59](https://www.npmjs.com/package/survey-pdf/v/1.12.59)
* [v2.5.5](https://www.npmjs.com/package/survey-pdf/v/2.5.5)

### Action

Users should upgrade `survey-pdf` in their projects to v1.12.59+ or v2.5.5+ immediately.

### Notes

No other `survey-pdf` dependencies are affected. This update is fully backward-compatible with previous `survey-pdf` releases.

## References
- https://github.com/parallax/jsPDF/security/advisories/GHSA-f8cm-6447-x5h2
- https://github.com/surveyjs/survey-pdf/security/advisories/GHSA-h3q6-jfrg-3x6q
- https://nvd.nist.gov/vuln/detail/CVE-2026-25630
- https://github.com/surveyjs/survey-pdf
