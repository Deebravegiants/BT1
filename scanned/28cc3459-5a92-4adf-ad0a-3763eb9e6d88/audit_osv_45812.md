# [M] JLSEC-2026-356

## Summary
Severity: Medium
Advisory: JLSEC-2026-356
Ecosystem: Julia
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/JLSEC-2026-356
Type: osv

## Affected
- Julia: `Gnuplot_jll` — affected >=0 <6.0.3000+0

## Details
A flaw was found in gnuplot. The GetAnnotateString() function may lead to a segmentation fault and cause a system crash.

## References
- https://access.redhat.com/security/cve/CVE-2025-31178
- https://bugzilla.redhat.com/show_bug.cgi?id=2355341
- https://sourceforge.net/p/gnuplot/bugs/2754/
