# [H] @discordjs/opus vulnerable to Denial of Service

## Summary
Severity: High
Advisory: GHSA-43wq-xrcm-3vgr
CVE: CVE-2024-21521
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-10
Source: https://github.com/advisories/GHSA-43wq-xrcm-3vgr
Type: github-advisory

## Affected
- npm: `@discordjs/opus` — affected >=0

## Details
All versions of the package @discordjs/opus are vulnerable to Denial of Service (DoS) due to providing an input object with a property toString to several different functions. Exploiting this vulnerability could lead to a process crash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21521
- https://gist.github.com/dellalibera/98c48fd74bb240adbd7841a5c02aba9e
- https://github.com/discordjs/opus
- https://github.com/discordjs/opus/blob/814e500c2785c5207ace19650192629beba2728b/src/node-opus.cc#L47
- https://security.snyk.io/vuln/SNYK-JS-DISCORDJSOPUS-6370643
