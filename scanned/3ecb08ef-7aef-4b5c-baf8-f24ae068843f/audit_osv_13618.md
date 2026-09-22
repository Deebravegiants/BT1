# [H] CVE-2018-20541

## Summary
Severity: High
Advisory: CVE-2018-20541
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-28
Source: https://osv.dev/vulnerability/CVE-2018-20541
Type: osv

## Details
There is a heap-based buffer overflow in libxsmm_sparse_csc_reader at generator_spgemm_csc_reader.c in LIBXSMM 1.10, a different vulnerability than CVE-2018-20542 (which is in a different part of the source code and is seen at different addresses).

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1652632
- https://github.com/hfp/libxsmm/commit/151481489192e6d1997f8bde52c5c425ea41741d
- https://github.com/hfp/libxsmm/issues/287
