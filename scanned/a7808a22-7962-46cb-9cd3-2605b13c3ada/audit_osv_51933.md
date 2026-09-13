# [M] CVE-2021-45833

## Summary
Severity: Medium
Advisory: CVE-2021-45833
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-05
Source: https://osv.dev/vulnerability/CVE-2021-45833
Type: osv

## Details
A Stack-based Buffer Overflow Vulnerability exists in HDF5 1.13.1-1 via the H5D__create_chunk_file_map_hyper function in /hdf5/src/H5Dchunk.c, which causes a Denial of Service (context-dependent).

## References
- https://github.com/HDFGroup/hdf5/issues/1313
