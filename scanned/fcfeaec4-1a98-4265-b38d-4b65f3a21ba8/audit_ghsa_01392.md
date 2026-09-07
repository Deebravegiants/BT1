# [M] Cross-Site Scripting in mavon-editor

## Summary
Severity: Medium
Advisory: GHSA-jfcc-rm7f-xgf8
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-jfcc-rm7f-xgf8
Type: github-advisory

## Affected
- npm: `mavon-editor` — affected >=0 <2.8.2

## Details
All versions of `mavon-editor` are vulnerable to Cross-Site Scripting. The package fails to sanitize entered input, allowing attackers to execute arbitrary JavaScript in a victim's browser.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://github.com/hinesboy/mavonEditor/issues/472
- https://github.com/hinesboy/mavonEditor/pull/548
- https://github.com/hinesboy/mavonEditor/commit/5592ec3761bd3b5a12ba6f99ce3c4057c6e33f72
- https://github.com/hinesboy/mavonEditor
- https://snyk.io/vuln/SNYK-JS-MAVONEDITOR-459108
- https://www.npmjs.com/advisories/1169
- https://www.npmjs.com/package/mavon-editor
