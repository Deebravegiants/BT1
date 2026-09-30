# [M] CVE-2018-20543

## Summary
Severity: Medium
Advisory: CVE-2018-20543
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-28
Source: https://osv.dev/vulnerability/CVE-2018-20543
Type: osv

## Details
There is an attempted excessive memory allocation at libxsmm_sparse_csc_reader in generator_spgemm_csc_reader.c in LIBXSMM 1.10 that will cause a denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1652634
