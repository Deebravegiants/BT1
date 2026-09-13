# [H] Multer vulnerable to Denial of Service via deeply nested field names

## Summary
Severity: High
Advisory: GHSA-72gw-mp4g-v24j
CVE: CVE-2026-5079
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-72gw-mp4g-v24j
Type: github-advisory

## Affected
- npm: `multer` — affected >=1.0.0 <2.2.0
- npm: `multer` — affected >=3.0.0-alpha.1 <3.0.0-alpha.2

## Details
### Impact

Multer is vulnerable to a Denial of Service (DoS) via deeply nested field names in multipart form data. The `append-field` dependency parses bracket notation in field names (e.g., `a[b][c]`) with no limit on nesting depth, allowing an attacker to force allocation of deeply nested object structures that consume CPU and memory. A single HTTP request with a crafted multipart body is sufficient to exploit this.

### Patches

Users should upgrade to `2.2.0` and configure `limits.fieldNestingDepth` to the minimum depth their application requires.

### Workarounds

Set `limits.fields` to a reasonable value to reduce the number of fields an attacker can send per request. This does not fully mitigate the issue but limits the impact.

## References
- https://github.com/expressjs/multer/security/advisories/GHSA-72gw-mp4g-v24j
- https://nvd.nist.gov/vuln/detail/CVE-2026-5079
- https://cna.openjsf.org/security-advisories.html
- https://github.com/expressjs/multer
