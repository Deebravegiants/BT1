# [H] CVE-2020-36428

## Summary
Severity: High
Advisory: CVE-2020-36428
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-07-20
Source: https://osv.dev/vulnerability/CVE-2020-36428
Type: osv

## Details
matio (aka MAT File I/O Library) 1.5.18 through 1.5.21 has a heap-based buffer overflow in ReadInt32DataDouble (called from ReadInt32Data and Mat_VarRead4).

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=21421
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/matio/OSV-2020-799.yaml
