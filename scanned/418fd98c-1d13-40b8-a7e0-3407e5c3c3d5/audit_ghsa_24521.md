# [H] Aubio Divide-By-Zero DoS vulnerability in new_aubio_source_wavread function

## Summary
Severity: High
Advisory: GHSA-vcwx-8mqh-2557
CVE: CVE-2017-17054
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-vcwx-8mqh-2557
Type: github-advisory

## Affected
- PyPI: `aubio` — affected >=0 <0.4.7

## Details
In aubio 0.4.6, a divide-by-zero error exists in the function `new_aubio_source_wavread()` in source_wavread.c, which may lead to DoS when playing a crafted audio file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-17054
- https://github.com/aubio/aubio/issues/148
- https://github.com/aubio/aubio/commit/25ecb7338cebc5b8c79092347839c78349ec33f1
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=883355
- https://github.com/aubio/aubio
- https://github.com/pypa/advisory-database/tree/main/vulns/aubio/PYSEC-2017-75.yaml
