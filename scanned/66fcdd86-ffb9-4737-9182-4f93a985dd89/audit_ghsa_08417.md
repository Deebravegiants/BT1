# [H] Pillow has an OOB Write with Invalid PSD Tile Extents (Integer Overflow)

## Summary
Severity: High
Advisory: GHSA-pwv6-vv43-88gr
CVE: CVE-2026-42311
CWE: CWE-190, CWE-787
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-pwv6-vv43-88gr
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=10.3.0 <12.2.0

## Details
### Impact
Processing a malicious PSD file could lead to memory corruption, potentially resulting in a crash or arbitrary code execution.

### Patches
Patched version: 12.2.0

Pillow 12.1.1 addressed CVE-2026-25990 by adding checks for tile extents in PSD image decoding/encoding to prevent an out-of-bounds write. However, the bounds checks computed tile extent sums using types susceptible to integer overflow, meaning a PSD image with carefully chosen tile dimensions could produce values that wrap around and bypass the checks, still triggering an out-of-bounds write in src/decode.c and src/encode.c. The fix avoids adding extents together before comparison.

### Workarounds
Use any version but affected versions: >= 10.3.0, < 12.2.0

### Resources
 - Fix: https://github.com/python-pillow/Pillow/pull/9520 
 - Original issue: CVE-2026-25990 (Pillow 12.1.1)

## References
- https://github.com/python-pillow/Pillow/security/advisories/GHSA-cfh3-3jmp-rvhc
- https://github.com/python-pillow/Pillow/security/advisories/GHSA-pwv6-vv43-88gr
- https://nvd.nist.gov/vuln/detail/CVE-2026-42311
- https://github.com/python-pillow/Pillow/pull/9520
- https://github.com/python-pillow/Pillow/commit/58f9a1d166dcb0c274807d4423522d205b0c35ea
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/releases/tag/12.2.0
