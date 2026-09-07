# [M] Liferay Portal Vulnerable to Cross-Site Scripting (XSS) via a Journal Article Title

## Summary
Severity: Medium
Advisory: GHSA-m2gx-7pvx-3gvg
CVE: CVE-2019-16147
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m2gx-7pvx-3gvg
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.journal.taglib` — affected >=0 <3.0.4

## Details
Liferay Portal through 7.2.0 GA1 allows XSS via a journal article title to `journal_article/page.jsp` in `journal/journal-taglib`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16147
- https://github.com/liferay/liferay-portal/commit/7e063aed70f947a92bb43a4471e0c4e650fe8f7f
- https://github.com/liferay/liferay-portal
