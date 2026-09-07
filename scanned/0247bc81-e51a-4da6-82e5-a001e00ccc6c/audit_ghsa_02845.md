# [M] Cross-site Scripting in Limesurvey

## Summary
Severity: Medium
Advisory: GHSA-h9ph-jcgh-gf69
CVE: CVE-2021-42112
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-h9ph-jcgh-gf69
Type: github-advisory

## Affected
- Packagist: `limesurvey/limesurvey` — affected >=0 <3.27.19

## Details
The "File upload question" functionality in LimeSurvey 3.x-LTS through 3.27.18 allows XSS in assets/scripts/modaldialog.js and assets/scripts/uploader.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42112
- https://github.com/LimeSurvey/LimeSurvey/pull/2044
- https://github.com/LimeSurvey/LimeSurvey/commit/d56619a50cfd191bbffd0adb660638a5e438070d
- https://bugs.limesurvey.org/view.php?id=17562
- https://github.com/LimeSurvey/LimeSurvey
- https://www.on-x.com/sites/default/files/on-x_-_security_advisory_-_limesurvey_-_cve-2021-42112.pdf
