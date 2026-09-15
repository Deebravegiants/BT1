# [H] CVE-2020-36430

## Summary
Severity: High
Advisory: CVE-2020-36430
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-07-20
Source: https://osv.dev/vulnerability/CVE-2020-36430
Type: osv

## Details
libass 0.15.x before 0.15.1 has a heap-based buffer overflow in decode_chars (called from decode_font and process_text) because the wrong integer data type is used for subtraction.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6JUXFQUJ32GWG5E46A63DFDCYJAF3VU6/
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/libass/OSV-2020-2099.yaml
- https://security.gentoo.org/glsa/202208-13
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=26674
- https://github.com/libass/libass/commit/017137471d0043e0321e377ed8da48e45a3ec632
