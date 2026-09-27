# [C] CVE-2026-51808

## Summary
Severity: Critical
Advisory: CVE-2026-51808
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-51808
Type: osv

## Details
Buffer Overflow vulnerability in OpenHTJ2K v.0.18.4 and before allows an attacker to execute arbitrary code via the openhtj2k_decoder_impl::invoke, invoke_line_based, invoke_line_based_stream, and invoke_line_based_predecoded function in source/core/interface/decoder.cpp

## References
- https://github.com/osamu620/OpenHTJ2K/blob/main/CHANGELOG
- https://github.com/osamu620/OpenHTJ2K/releases/tag/v0.18.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/51xxx/CVE-2026-51808.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-51808
- https://github.com/osamu620/OpenHTJ2K/pull/320
