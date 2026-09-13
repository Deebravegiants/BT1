# [H] JLSEC-2026-354

## Summary
Severity: High
Advisory: JLSEC-2026-354
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-354
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=0 <1.14.2+0

## Details
HDF5 is software for managing data. In 1.14.1-2 and earlier, a heap-use-after-free was found in the h5dump helper utility. An attacker who can supply a malicious h5 file can trigger a heap use-after-free. The freed object is referenced in a memmove call from `H5T__conv_struct`. The original object was allocated by `H5D__typeinfo_init_phase3` and freed by `H5D__typeinfo_term`.

## References
- https://access.redhat.com/security/cve/CVE-2026-34734
- https://bugzilla.redhat.com/show_bug.cgi?id=2457034
- https://github.com/HDFGroup/hdf5/security/advisories/GHSA-w7v2-9cmr-pwwj
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-34734.json
