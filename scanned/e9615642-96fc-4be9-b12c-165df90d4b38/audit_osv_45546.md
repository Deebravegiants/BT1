# [M] JLSEC-2026-1294

## Summary
Severity: Medium
Advisory: JLSEC-2026-1294
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1294
Type: osv

## Affected
- Julia: `libxls_jll` — affected >=0 <1.6.2+0

## Details
An issue was discovered in libxls before and including 1.6.1 when reading Microsoft Excel files. A NULL pointer dereference vulnerability exists when parsing XLS cells in `libxls/xls2csv.c:199`. It could allow a remote attacker to cause a denial of service via crafted XLS file.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1903296
- https://bugzilla.redhat.com/show_bug.cgi?id=1903296
