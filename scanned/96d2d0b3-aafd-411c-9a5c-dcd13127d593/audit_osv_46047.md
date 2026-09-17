# [H] JLSEC-2026-604

## Summary
Severity: High
Advisory: JLSEC-2026-604
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/JLSEC-2026-604
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <16.14.0+0

## Details
Use of inherently dangerous function `PQfn(..., result_is_int=0, ...)` in PostgreSQL libpq `lo_export()`, `lo_read()`, `lo_lseek64()`, and `lo_tell64()` functions allows the server superuser to overwrite a client stack buffer with an arbitrarily-large response.  Like `gets()`, `PQfn(..., result_is_int=0, ...)` stores arbitrary-length, server-determined data into a buffer of unspecified size.  Because both the `\lo_export` command in psql and `pg_dump` call `lo_read()`, the server superuser can overwrite `pg_dump` or psql stack memory.  Versions before PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 are affected.

## References
- https://access.redhat.com/errata/RHSA-2026:21182
- https://access.redhat.com/errata/RHSA-2026:22878
- https://access.redhat.com/errata/RHSA-2026:26181
- https://access.redhat.com/errata/RHSA-2026:26203
- https://access.redhat.com/errata/RHSA-2026:26204
- https://access.redhat.com/errata/RHSA-2026:26524
- https://access.redhat.com/errata/RHSA-2026:26525
- https://access.redhat.com/errata/RHSA-2026:26561
- https://access.redhat.com/errata/RHSA-2026:27718
- https://access.redhat.com/errata/RHSA-2026:27738
- https://access.redhat.com/errata/RHSA-2026:27741
- https://access.redhat.com/errata/RHSA-2026:27742
- https://access.redhat.com/errata/RHSA-2026:27743
- https://access.redhat.com/errata/RHSA-2026:28037
- https://access.redhat.com/errata/RHSA-2026:28143
- https://access.redhat.com/errata/RHSA-2026:28208
- https://access.redhat.com/errata/RHSA-2026:28999
- https://access.redhat.com/errata/RHSA-2026:29212
- https://access.redhat.com/errata/RHSA-2026:29815
- https://access.redhat.com/errata/RHSA-2026:29904
