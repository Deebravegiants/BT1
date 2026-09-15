# [C] media: dvb-net: fix OOB access in ULE extension header tables

## Summary
Severity: Critical
Advisory: CVE-2026-31405
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-31405
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: dvb-net: fix OOB access in ULE extension header tables

The ule_mandatory_ext_handlers[] and ule_optional_ext_handlers[] tables
in handle_one_ule_extension() are declared with 255 elements (valid
indices 0-254), but the index htype is derived from network-controlled
data as (ule_sndu_type & 0x00FF), giving a range of 0-255. When
htype equals 255, an out-of-bounds read occurs on the function pointer
table, and the OOB value may be called as a function pointer.

Add a bounds check on htype against the array size before either table
is accessed. Out-of-range values now cause the SNDU to be discarded.

## References
- https://git.kernel.org/stable/c/145e50c2c700fa52b840df7bab206043997dd18e
- https://git.kernel.org/stable/c/1a6da3dbb9985d00743073a1cc1f96e59f5abc30
- https://git.kernel.org/stable/c/24d87712727a5017ad142d63940589a36cd25647
- https://git.kernel.org/stable/c/29ef43ceb121d67b87f4cbb08439e4e9e732eff8
- https://git.kernel.org/stable/c/8bde543d2a5f935ba2a6a6325a2e02f8a9256fbe
- https://git.kernel.org/stable/c/b2bd2ee73b697c177157bba534e1b1064c2e66a0
- https://git.kernel.org/stable/c/e51238718217c4abdb3ccc3b0c0cde265c7ec629
- https://git.kernel.org/stable/c/f2b65dcb78c8990e4c68a906627433be1fe38a92
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31405.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31405
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
