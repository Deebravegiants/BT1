# [H] File restriction bypass in socket.io-file

## Summary
Severity: High
Advisory: GHSA-6495-8jvh-f28x
CVE: CVE-2020-24807
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-10-02
Source: https://github.com/advisories/GHSA-6495-8jvh-f28x
Type: github-advisory

## Affected
- npm: `socket.io-file` — affected >=0

## Details
All versions of `socket.io-file`are vulnerable to a file restriction bypass. The validation for valid file types only happens on the client-side, which allows an attacker to intercept the Websocket request post-validation and alter the `name` value to upload any file types.

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24807
- https://github.com/rico345100/socket.io-file
- https://www.npmjs.com/advisories/1564
