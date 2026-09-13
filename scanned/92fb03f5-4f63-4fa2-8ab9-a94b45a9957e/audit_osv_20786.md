# [M] CVE-2021-36977

## Summary
Severity: Medium
Advisory: CVE-2021-36977
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-07-20
Source: https://osv.dev/vulnerability/CVE-2021-36977
Type: osv

## Details
matio (aka MAT File I/O Library) 1.5.20 and 1.5.21 has a heap-based buffer overflow in H5MM_memcpy (called from H5MM_malloc and H5C_load_entry), related to use of HDF5 1.12.0.

## References
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/matio/OSV-2021-440.yaml
- https://github.com/HDFGroup/hdf5/issues/272
- https://github.com/google/oss-fuzz/issues/4999
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=31265
- https://github.com/google/oss-fuzz-vulns/commit/37b781ace1b4228fc36483bb7e30c72ea9d4c3d6
