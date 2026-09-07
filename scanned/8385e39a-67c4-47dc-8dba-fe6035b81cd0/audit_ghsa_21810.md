# [M] Cross-site scripting in @atlaskit/editor-core

## Summary
Severity: Medium
Advisory: GHSA-p5ch-w78f-xh44
CVE: CVE-2019-20903
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-p5ch-w78f-xh44
Type: github-advisory

## Affected
- npm: `@atlaskit/editor-core` — affected >=0

## Details
The hyperlinks functionality in atlaskit/editor-core in before version 113.1.5 allows remote attackers to inject arbitrary HTML or JavaScript via a Cross-Site Scripting (XSS) vulnerability in link targets.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-20903
- https://atlaskit.atlassian.com/packages/editor/editor-core/changelog/113.1.5
- https://bitbucket.org/atlassian/atlaskit-mk-2/commits/ca88f616e4
- https://confluence.atlassian.com/pages/viewpage.action?pageId=1021244735
- https://www.npmjs.com/package/@atlaskit/editor-core
