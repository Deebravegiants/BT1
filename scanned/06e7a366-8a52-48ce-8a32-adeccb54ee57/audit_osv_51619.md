# [H] CVE-2021-36089

## Summary
Severity: High
Advisory: CVE-2021-36089
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-07-01
Source: https://osv.dev/vulnerability/CVE-2021-36089
Type: osv

## Details
Grok 7.6.6 through 9.2.0 has a heap-based buffer overflow in grk::FileFormatDecompress::apply_palette_clr (called from grk::FileFormatDecompress::applyColour).

## References
- https://github.com/GrokImageCompression/grok/releases
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/grok/OSV-2021-677.yaml
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=33544
