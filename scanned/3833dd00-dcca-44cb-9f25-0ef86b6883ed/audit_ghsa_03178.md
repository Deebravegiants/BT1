# [H] Regular Expression Denial of Service in dat.gui

## Summary
Severity: High
Advisory: GHSA-chwr-hf3w-c984
CVE: CVE-2020-7755
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-chwr-hf3w-c984
Type: github-advisory

## Affected
- npm: `dat.gui` — affected >=0

## Details
All versions of package dat.gui are vulnerable to Regular Expression Denial of Service (ReDoS) via specifically crafted rgb and rgba values.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7755
- https://github.com/dataarts/dat.gui/issues/278
- https://github.com/dataarts/dat.gui/pull/279
- https://snyk.io/vuln/SNYK-JS-DATGUI-1016275
- https://www.npmjs.com/package/dat.gui
