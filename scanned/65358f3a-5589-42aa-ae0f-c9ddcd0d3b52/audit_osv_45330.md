# [M] In GnuPG before 2.5.5, if a user chooses to import a certificate with certain crafted subkey data...

## Summary
Severity: Medium
Advisory: JLSEC-2025-94
Ecosystem: Julia
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/JLSEC-2025-94
Type: osv

## Affected
- Julia: `GnuPG_jll` — affected >=0 <2.4.8+0

## Details
In GnuPG before 2.5.5, if a user chooses to import a certificate with certain crafted subkey data that lacks a valid backsig or that has incorrect usage flags, the user loses the ability to verify signatures made from certain other signing keys, aka a "verification DoS."

## References
- https://dev.gnupg.org/T7527
- https://dev.gnupg.org/rG48978ccb4e20866472ef18436a32744350a65158
- https://lists.gnupg.org/pipermail/gnupg-announce/2025q1/000491.html
