# [H] JLSEC-2026-487

## Summary
Severity: High
Advisory: JLSEC-2026-487
Ecosystem: Julia
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-487
Type: osv

## Affected
- Julia: `Glib_jll` — affected >=0 <2.86.3+0

## Details
A heap-based buffer overflow problem was found in glib through an incorrect calculation of buffer size in the `g_escape_uri_string()` function. If the string to escape contains a very large number of unacceptable characters (which would need escaping), the calculation of the length of the escaped string could overflow, leading to a potential write off the end of the newly allocated string.

## References
- https://access.redhat.com/errata/RHSA-2026:0936
- https://access.redhat.com/errata/RHSA-2026:0975
- https://access.redhat.com/errata/RHSA-2026:0991
- https://access.redhat.com/errata/RHSA-2026:1323
- https://access.redhat.com/errata/RHSA-2026:1324
- https://access.redhat.com/errata/RHSA-2026:1326
- https://access.redhat.com/errata/RHSA-2026:1327
- https://access.redhat.com/errata/RHSA-2026:1465
- https://access.redhat.com/errata/RHSA-2026:1608
- https://access.redhat.com/errata/RHSA-2026:1624
- https://access.redhat.com/errata/RHSA-2026:1625
- https://access.redhat.com/errata/RHSA-2026:1626
- https://access.redhat.com/errata/RHSA-2026:1627
- https://access.redhat.com/errata/RHSA-2026:1652
- https://access.redhat.com/errata/RHSA-2026:1736
- https://access.redhat.com/errata/RHSA-2026:18344
- https://access.redhat.com/errata/RHSA-2026:18705
- https://access.redhat.com/errata/RHSA-2026:2064
- https://access.redhat.com/errata/RHSA-2026:2072
- https://access.redhat.com/errata/RHSA-2026:2485
