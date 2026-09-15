# [M] CVE-2019-20792

## Summary
Severity: Medium
Advisory: CVE-2019-20792
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-29
Source: https://osv.dev/vulnerability/CVE-2019-20792
Type: osv

## Details
OpenSC before 0.20.0 has a double free in coolkey_free_private_data because coolkey_add_object in libopensc/card-coolkey.c lacks a uniqueness check.

## References
- https://github.com/OpenSC/OpenSC/compare/0.19.0...0.20.0
- https://github.com/OpenSC/OpenSC/commit/c246f6f69a749d4f68626b40795a4f69168008f4
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=19208
