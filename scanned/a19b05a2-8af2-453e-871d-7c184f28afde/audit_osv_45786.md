# [H] JLSEC-2026-325

## Summary
Severity: High
Advisory: JLSEC-2026-325
Ecosystem: Julia
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-325
Type: osv

## Affected
- Julia: `HDF5_jll` — affected >=1.14.5+0 <2.0.0+0

## Details
A vulnerability, which was classified as critical, was found in HDF5 1.14.6. Affected is the function `H5SM_delete` of the file H5SM.c of the component h5 File Handler. The manipulation leads to heap-based buffer overflow. It is possible to launch the attack remotely. The complexity of an attack is rather high. The exploitability is told to be difficult. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/HDFGroup/hdf5/issues/5329
- https://github.com/sae-as-me/Crashes/raw/refs/heads/main/hdf5/h5_extended_crash.h5
- https://vuldb.com/?ctiid.299064
- https://vuldb.com/?id.299064
- https://vuldb.com/?submit.510819
