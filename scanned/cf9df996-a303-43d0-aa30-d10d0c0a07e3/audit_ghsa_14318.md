# [M] Regular Expression Denial of Service in Deno.upgradeWebSocket API

## Summary
Severity: Medium
Advisory: GHSA-jc97-h3h9-7xh6
CVE: CVE-2023-26103
CWE: CWE-1333
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-04-03
Source: https://github.com/advisories/GHSA-jc97-h3h9-7xh6
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=1.12.0 <1.31.0

## Details
### Impact
Versions of the package deno before 1.31.0 are vulnerable to Regular Expression Denial of Service (ReDoS) due to the upgradeWebSocket function, which contains regexes in the form of /s*,s*/, used for splitting the Connection/Upgrade header. A specially crafted Connection/Upgrade header can be used to significantly slow down a web socket server. 

### Patches
It is recommended that users upgrade to Deno 1.31.0.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-jc97-h3h9-7xh6
- https://nvd.nist.gov/vuln/detail/CVE-2023-26103
- https://github.com/denoland/deno/pull/17722
- https://github.com/denoland/deno/commit/cf06a7c7e672880e1b38598fe445e2c50b4a9d06
- https://github.com/denoland/deno
- https://github.com/denoland/deno/blob/2b247be517d789a37e532849e2e40b724af0918f/ext/http/01_http.js#L395-L409
- https://github.com/denoland/deno/releases/tag/v1.31.0
- https://security.snyk.io/vuln/SNYK-RUST-DENO-3315970
