# [H] lol-html panics on certain HTML inputs

## Summary
Severity: High
Advisory: GHSA-c3x7-354f-4p2x
CVE: CVE-2023-4241
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-08-09
Source: https://github.com/advisories/GHSA-c3x7-354f-4p2x
Type: github-advisory

## Affected
- crates.io: `lol-html` — affected >=0 <1.1.1

## Details
### Impact
lol-html can cause panics on certain HTML inputs. Anyone processing arbitrary 3rd party HTML with the library is affected.

### Patches
The problem has been patched and released as v1.1.1

### Workarounds
No workarounds exist.

## References
- https://github.com/cloudflare/lol-html/security/advisories/GHSA-c3x7-354f-4p2x
- https://nvd.nist.gov/vuln/detail/CVE-2023-4241
- https://github.com/cloudflare/lol-html
