# [M] Cross-site scripting in Survey Creator

## Summary
Severity: Medium
Advisory: GHSA-xgj4-2hrf-j4xg
CVE: CVE-2024-28635
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-21
Source: https://github.com/advisories/GHSA-xgj4-2hrf-j4xg
Type: github-advisory

## Affected
- npm: `survey-creator` — affected >=0 <1.9.133

## Details
Cross Site Scripting (XSS) vulnerability in SurveyJS Survey Creator v.1.9.132 and before, allows attackers to execute arbitrary code and obtain sensitive information via the title parameter in form.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28635
- https://github.com/surveyjs/survey-creator/issues/5285
- https://github.com/surveyjs/survey-creator
- https://packetstormsecurity.com/2403-exploits/surveyjssurveycreator19132-xss.txt
