# [M] Cross-Site Scripting in @ckeditor/ckeditor5-link

## Summary
Severity: Medium
Advisory: GHSA-gvpx-9459-w3mj
CVE: CVE-2018-11093
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-05-23
Source: https://github.com/advisories/GHSA-gvpx-9459-w3mj
Type: github-advisory

## Affected
- npm: `@ckeditor/ckeditor5-link` — affected >=0.3.0 <10.0.1

## Details
Versions of `status-board` prior to 10.0.1 are vulnerable to Cross-Site Scripting. The `_createPreviewButton()` function fails to sanitize the `href` attribute of a created `<a>` tag. This may allow attackers to execute arbitrary JavaScript in a victim's browser.


## Recommendation

Upgrade to version 10.0.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11093
- https://github.com/ckeditor/ckeditor5-link/commit/8cb782eceba10fc481e4021cb5d25b2a85d1b04e
- https://ckeditor.com/blog/CKEditor-5-v10.0.1-released
- https://github.com/advisories/GHSA-gvpx-9459-w3mj
- https://github.com/ckeditor/ckeditor5-link
- https://github.com/ckeditor/ckeditor5-link/blob/master/CHANGELOG.md#1001-2018-05-22
- https://snyk.io/vuln/SNYK-JS-CKEDITORCKEDITOR5LINK-72892
- https://www.npmjs.com/advisories/1154
