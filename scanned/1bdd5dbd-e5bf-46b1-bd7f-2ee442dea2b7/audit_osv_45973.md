# [C] JLSEC-2026-532

## Summary
Severity: Critical
Advisory: JLSEC-2026-532
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-532
Type: osv

## Affected
- Julia: `Lz4_jll` — affected >=0 <1.9.4+0

## Details
There's a flaw in lz4. An attacker who submits a crafted file to an application linked with lz4 may be able to trigger an integer overflow, leading to calling of memmove() on a negative size argument, causing an out-of-bounds write and/or a crash. The greatest impact of this flaw is to availability, with some potential impact to confidentiality and integrity as well.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1954559
- https://security.netapp.com/advisory/ntap-20211104-0005/
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
