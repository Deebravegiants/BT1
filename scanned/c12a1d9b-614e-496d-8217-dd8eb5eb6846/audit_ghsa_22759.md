# [H] Asterix Heap-based Buffer Overflow

## Summary
Severity: High
Advisory: GHSA-6mmf-v5q7-vw2w
CVE: CVE-2021-44144
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6mmf-v5q7-vw2w
Type: github-advisory

## Affected
- PyPI: `asterix_decoder` — affected >=0 <0.7.2

## Details
Croatia Control Asterix 2.8.1 has a heap-based buffer over-read, with additional details to be disclosed at a later date.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44144
- https://github.com/CroatiaControlLtd/asterix/issues/183
- https://github.com/CroatiaControlLtd/asterix/commit/3f765d387d239ccc44e278a2ffa600fb6a6587f9
- https://github.com/CroatiaControlLtd/asterix
- https://github.com/CroatiaControlLtd/asterix/blob/daf33de522d1cdab0e941c025b89e18a0d4d42c6/README.md?plain=1#L7
- https://github.com/pypa/advisory-database/tree/main/vulns/asterix-decoder/PYSEC-2021-860.yaml
- https://web.archive.org/web/20221207104133/https://huntr.dev/bounties/1-other-CroatiaControlLtd/asterix
