# [M] CVE-2025-30258

## Summary
Severity: Medium
Advisory: CVE-2025-30258
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-19
Source: https://osv.dev/vulnerability/CVE-2025-30258
Type: osv

## Details
In GnuPG before 2.5.5, if a user chooses to import a certificate with certain crafted subkey data that lacks a valid backsig or that has incorrect usage flags, the user loses the ability to verify signatures made from certain other signing keys, aka a "verification DoS."

## References
- https://lists.gnupg.org/pipermail/gnupg-announce/2025q1/000491.html
- https://dev.gnupg.org/rG48978ccb4e20866472ef18436a32744350a65158
- https://dev.gnupg.org/T7527
