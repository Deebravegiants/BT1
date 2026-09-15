# [C] JLSEC-2026-714

## Summary
Severity: Critical
Advisory: JLSEC-2026-714
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-714
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
Two potential heap out-of-bounds write locations existed in DecodeObjectId() in `wolfcrypt/src/asn.c`. First, a bounds check only validates one available slot before writing two OID arc values (out[0] and out[1]), enabling a 2-byte out-of-bounds write when outSz equals 1. Second, multiple callers pass sizeof(decOid) (64 bytes on 64-bit platforms) instead of the element count `MAX_OID_SZ` (32), causing the function to accept crafted OIDs with 33 or more arcs that write past the end of the allocated buffer.

## References
- https://github.com/wolfSSL/wolfssl
