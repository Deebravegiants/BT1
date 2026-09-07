# [M] Improper Verification of Communication Channel in @theia/plugin-ext

## Summary
Severity: Medium
Advisory: GHSA-w6v7-w58j-pg5r
CVE: CVE-2021-41038
CWE: CWE-940
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-11-15
Source: https://github.com/advisories/GHSA-w6v7-w58j-pg5r
Type: github-advisory

## Affected
- npm: `@theia/plugin-ext` — affected >=0 <1.18.0

## Details
In versions of the @theia/plugin-ext component of Eclipse Theia prior to 1.18.0, Webview contents can be hijacked via postMessage().

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41038
- https://github.com/eclipse-theia/theia/pull/10125
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=575924
- https://github.com/eclipse-theia/theia
