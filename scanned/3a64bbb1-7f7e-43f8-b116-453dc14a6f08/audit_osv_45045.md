# [M] EC public key out of bounds read

## Summary
Severity: Medium
Advisory: OSEC-2026-15
Aliases: CVE-2026-87736
Ecosystem: opam
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/OSEC-2026-15
Type: osv

## Affected
- opam: `mirage-crypto-ec` — affected >=0 <2.3.0, >=0 <1f0bf67044e67cf6e46911fcd77a0ff706b6c3e7

## Details
The internal Point.of_octets function is missing a length check for compressed
points, and thus is raising an exception when a short buffer is provided. This
affects all NIST curves (P-256, P-384, P-521) and both `Dsa.pub_of_octets` and
`Dh.key_exchange` functions.

## Fix

The fix is to check the length of the provided buffer.

## Timeline

- July 28th 2026: report to security@ocaml.org
- August 7th: release of mirage-crypto-pk 2.3.0 and security advisory
