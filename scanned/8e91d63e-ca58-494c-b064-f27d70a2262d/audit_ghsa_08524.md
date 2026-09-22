# [M] electerm's encrypt method not safe enough

## Summary
Severity: Medium
Advisory: GHSA-g29v-q6h7-76wh
CVE: CVE-2026-45787
CWE: CWE-326, CWE-329, CWE-353, CWE-759, CWE-916
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-g29v-q6h7-76wh
Type: github-advisory

## Affected
- npm: `electerm` — affected >=0 <3.9.5

## Details
### Impact
_Insecure sync encryption: deterministic AES-192-CBC with a fixed zero IV, constant KDF salt, and no MAC leads to confidentiality and integrity failures for synced bookmark/profile data. Attackers can crack common passwords across installs and perform undetected ciphertext bit-flips to alter config/bookmarks._

### Patches

- https://github.com/electerm/electerm/commit/9dd8295e37d53396b980cd45dfc5ed11ad79b937

### Workarounds

- No

### References
- Report / credit: https://github.com/Curly-Haired-Baboon
- Electerm releases: https://github.com/electerm/electerm/releases

## References
- https://github.com/electerm/electerm/security/advisories/GHSA-g29v-q6h7-76wh
- https://nvd.nist.gov/vuln/detail/CVE-2026-45787
- https://github.com/electerm/electerm/commit/9dd8295e37d53396b980cd45dfc5ed11ad79b937
- https://github.com/electerm/electerm
- https://github.com/electerm/electerm/releases/tag/v3.9.5
