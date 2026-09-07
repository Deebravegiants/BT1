# [M] Dash apps vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-547x-748v-vp6p
CVE: CVE-2024-21485
CWE: CWE-79
Ecosystem: PyPI, npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2024-02-02
Source: https://github.com/advisories/GHSA-547x-748v-vp6p
Type: github-advisory

## Affected
- npm: `dash-core-components` — affected >=0 <2.13.0
- PyPI: `dash-html-components` — affected >=0 <2.0.0
- PyPI: `dash-core-components` — affected >=0 <2.0.0
- PyPI: `dash` — affected >=0 <2.15.0
- npm: `dash-html-components` — affected >=0 <2.0.16

## Details
Versions of the package dash-core-components before 2.13.0; versions of the package dash-core-components before 2.0.0; versions of the package dash before 2.15.0; versions of the package dash-html-components before 2.0.0; versions of the package dash-html-components before 2.0.16 are vulnerable to Cross-site Scripting (XSS) when the href of the a tag is controlled by an adversary. An authenticated attacker who stores a view that exploits this vulnerability could steal the data that's visible to another user who opens that view - not just the data already included on the page, but they could also, in theory, make additional requests and access other data accessible to this user. In some cases, they could also steal the access tokens of that user, which would allow the attacker to act as that user, including viewing other apps and resources hosted on the same server. 

**Note:** 

This is only exploitable in Dash apps that include some mechanism to store user input to be reloaded by a different user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21485
- https://github.com/plotly/dash/issues/2729
- https://github.com/plotly/dash/pull/2732
- https://github.com/plotly/dash/commit/9920073c9a8619ae8f90fcec1924f2f3a4332a8c
- https://github.com/advisories/GHSA-547x-748v-vp6p
- https://github.com/plotly/dash
- https://github.com/plotly/dash/releases/tag/v2.15.0
- https://github.com/pypa/advisory-database/tree/main/vulns/dash-core-components/PYSEC-2026-219.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/dash-html-components/PYSEC-2026-220.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/dash/PYSEC-2024-35.yaml
- https://security.snyk.io/vuln/SNYK-JS-DASHCORECOMPONENTS-6183084
- https://security.snyk.io/vuln/SNYK-JS-DASHHTMLCOMPONENTS-6226337
- https://security.snyk.io/vuln/SNYK-PYTHON-DASH-6226335
- https://security.snyk.io/vuln/SNYK-PYTHON-DASHCORECOMPONENTS-6226334
- https://security.snyk.io/vuln/SNYK-PYTHON-DASHHTMLCOMPONENTS-6226336
