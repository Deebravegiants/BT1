# [M] Seafile Server has multiple stored XSS vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-rqj3-x344-qvxc
CVE: CVE-2026-30587
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-rqj3-x344-qvxc
Type: github-advisory

## Affected
- npm: `@seafile/sdoc-editor` — affected >=3.0.0 <3.0.75
- npm: `@seafile/sdoc-editor` — affected >=0 <2.0.209

## Details
Multiple Stored XSS vulnerabilities exist in Seafile Server version 13.0.15,13.0.16-pro,12.0.14 and prior and fixed in 13.0.17, 13.0.17-pro, and 12.0.20-pro, via the Seadoc (sdoc) editor. The application fails to properly sanitize WebSocket messages regarding document structure updates. This allows authenticated remote attackers to inject malicious JavaScript payloads via the src attribute of embedded Excalidraw whiteboards or the href attribute of anchor tags.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-30587
- https://github.com/haiwen/seadoc-editor/commit/8fa988aaede072b2ae073d1b2edcb2fc691423b2
- https://github.com/haiwen/seahub/commit/4c5301747bdb84c64b2f2b3230417df2d1cc8987
- https://gist.github.com/gabdevele/1b7e30ab367b26042fa32f45aa12ce2f
- https://github.com/haiwen/seadoc-editor
- https://manual.seafile.com/12.0/changelog/changelog-for-seafile-professional-server
- https://manual.seafile.com/13.0/changelog/changelog-for-seafile-professional-server
- https://manual.seafile.com/13.0/changelog/server-changelog
