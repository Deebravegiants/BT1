# [H] Integer Overflow in png-img

## Summary
Severity: High
Advisory: GHSA-q5wr-fvpq-p67g
CVE: CVE-2020-28248
CWE: CWE-190, CWE-787
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-10
Source: https://github.com/advisories/GHSA-q5wr-fvpq-p67g
Type: github-advisory

## Affected
- npm: `png-img` — affected >=0 <3.1.0

## Details
An integer overflow in the PngImg::InitStorage_() function of png-img before 3.1.0 leads to an under-allocation of heap memory and subsequently an exploitable heap-based buffer overflow when loading a crafted PNG file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28248
- https://github.com/gemini-testing/png-img/commit/14ac462a32ca4b3b78f56502ac976d5b0222ce3d
- https://github.com/gemini-testing/png-img
- https://github.com/gemini-testing/png-img/compare/v3.0.0...v3.1.0
- https://securitylab.github.com/advisories/GHSL-2020-142-gemini-png-img
