# [H] copyparty allows Regex Denial of Service (ReDoS) in the upload listing

## Summary
Severity: High
Advisory: GHSA-5662-2rj7-f2v6
CVE: CVE-2025-54796
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-08-04
Source: https://github.com/advisories/GHSA-5662-2rj7-f2v6
Type: github-advisory

## Affected
- PyPI: `copyparty` — affected >=0 <1.18.9

## Details
### Summary
The `filter` parameter for the "Recent uploads" page allows arbitrary Regexes. If this feature is enabled (which is the default), an attacker can craft a filter which deadlocks the server.

### PoC
`https://127.0.0.1:3923/?ru&filter=(.+)+x`

### Impact
The server becomes fully inaccessible for a long time.

## References
- https://github.com/9001/copyparty/security/advisories/GHSA-5662-2rj7-f2v6
- https://nvd.nist.gov/vuln/detail/CVE-2025-54796
- https://github.com/9001/copyparty/commit/09910ba80784c3980947d92f45db696398c0fd83
- https://github.com/9001/copyparty
- https://github.com/9001/copyparty/releases/tag/v1.18.9
