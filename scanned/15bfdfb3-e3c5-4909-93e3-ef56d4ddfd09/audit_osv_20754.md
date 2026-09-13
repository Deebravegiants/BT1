# [M] CVE-2021-36692

## Summary
Severity: Medium
Advisory: CVE-2021-36692
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-30
Source: https://osv.dev/vulnerability/CVE-2021-36692
Type: osv

## Details
libjxl v0.3.7 is affected by a Divide By Zero in issue in lib/extras/codec_apng.cc jxl::DecodeImageAPNG(). When encoding a malicous APNG file using cjxl, an attacker can trigger a denial of service.

## References
- https://github.com/libjxl/libjxl/issues/308
- https://github.com/libjxl/libjxl/commit/7dfa400ded53919d986c5d3d23446a09e0cf481b
- https://github.com/libjxl/libjxl/pull/313
