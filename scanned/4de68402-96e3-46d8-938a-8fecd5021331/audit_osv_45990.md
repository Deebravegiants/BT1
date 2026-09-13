# [M] JLSEC-2026-548

## Summary
Severity: Medium
Advisory: JLSEC-2026-548
Ecosystem: Julia
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-548
Type: osv

## Affected
- Julia: `OpenJpeg_jll` — affected >=2.5.0+0 <2.5.2+0

## Details
A flaw was found in OpenJPEG. Maliciously constructed pictures can cause the program to enter a large loop and continuously print warning messages on the terminal.

## References
- https://access.redhat.com/errata/RHSA-2026:4128
- https://access.redhat.com/security/cve/CVE-2023-39327
- https://bugzilla.redhat.com/show_bug.cgi?id=2295812
