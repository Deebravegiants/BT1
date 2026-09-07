# [M] ouqiang gocron Cross-site scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r947-2crg-xc39
CVE: CVE-2022-40365
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-15
Source: https://github.com/advisories/GHSA-r947-2crg-xc39
Type: github-advisory

## Affected
- Go: `github.com/ouqiang/gocron` — affected >=0

## Details
Cross site scripting (XSS) vulnerability in ouqiang gocron through 1.5.3, allows attackers to execute arbitrary code via scope.row.hostname in web/vue/src/pages/taskLog/list.vue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40365
- https://github.com/ouqiang/gocron/issues/362
- https://github.com/ouqiang/gocron
