# [M] A vulnerability was found in libarchive up to 3.7.7

## Summary
Severity: Medium
Advisory: JLSEC-2025-242
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-242
Type: osv

## Affected
- Julia: `LibArchive_jll` — affected >=0 <3.7.9+0

## Details
A vulnerability was found in libarchive up to 3.7.7. It has been classified as problematic. This affects the function list of the file bsdunzip.c. The manipulation leads to null pointer dereference. It is possible to launch the attack on the local host. The exploit has been disclosed to the public and may be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://github.com/Ekkosun/pocs/blob/main/bsdunzip-poc
- https://vuldb.com/?ctiid.296619
- https://vuldb.com/?id.296619
- https://vuldb.com/?submit.496460
