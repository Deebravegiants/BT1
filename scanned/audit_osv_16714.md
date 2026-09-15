# [H] CVE-2019-9151

## Summary
Severity: High
Advisory: CVE-2019-9151
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-25
Source: https://osv.dev/vulnerability/CVE-2019-9151
Type: osv

## Details
An issue was discovered in the HDF HDF5 1.10.4 library. There is an out of bounds read in the function H5VM_memcpyvv in H5VM.c when called from H5D__compact_readvv in H5Dcompact.c.

## References
- https://github.com/magicSwordsMan/PAAFS/tree/master/vul7
