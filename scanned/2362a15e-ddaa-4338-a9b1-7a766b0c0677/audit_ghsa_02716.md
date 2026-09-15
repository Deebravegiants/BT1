# [H] Remote code execution in Eclipse Theia

## Summary
Severity: High
Advisory: GHSA-v9w2-v7j9-rjpr
CVE: CVE-2021-34435
CWE: CWE-346, CWE-668, CWE-942
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-v9w2-v7j9-rjpr
Type: github-advisory

## Affected
- npm: `@theia/mini-browser` — affected >=0.3.9 <1.9.0

## Details
In Eclipse Theia 0.3.9 to 1.8.1, the "mini-browser" extension allows a user to preview HTML files in an iframe inside the IDE. But with the way it is made it is possible for a previewed HTML file to trigger an RCE. This exploit only happens if a user previews a malicious file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-34435
- https://github.com/eclipse-theia/theia/pull/8759
- https://github.com/eclipse-theia/theia/commit/0761dcf5fe3c14c27432683d42d2c526ad0cfbd5
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=568018
- https://github.com/eclipse-theia/theia
