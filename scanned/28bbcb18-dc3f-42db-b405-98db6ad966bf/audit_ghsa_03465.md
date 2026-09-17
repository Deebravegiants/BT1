# [H] Insufficient Verification of Data Authenticity in Eclipse Theia

## Summary
Severity: High
Advisory: GHSA-f7vx-j8mp-3h2x
CVE: CVE-2019-17636
CWE: CWE-345
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-f7vx-j8mp-3h2x
Type: github-advisory

## Affected
- npm: `@theia/mini-browser` — affected >=0.3.9 <0.16.0

## Details
In Eclipse Theia versions 0.3.9 through 0.15.0, one of the default pre-packaged Theia extensions is "Mini-Browser", published as "@theia/mini-browser" on npmjs.com. This extension, for its own needs, exposes a HTTP endpoint that allows to read the content of files on the hosts filesystem, given their path, without restrictions on the requesters origin. This design is vulnerable to being exploited remotely through a DNS rebinding attack or a drive-by download of a carefully crafted exploit.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17636
- https://github.com/eclipse-theia/theia/pull/7205
- https://github.com/eclipse-theia/theia/commit/b212d07f915df1509180944ee3132714bc2636bf
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=551747
