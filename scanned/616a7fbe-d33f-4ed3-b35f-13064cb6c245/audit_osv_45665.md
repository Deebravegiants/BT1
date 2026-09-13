# [H] JLSEC-2026-179

## Summary
Severity: High
Advisory: JLSEC-2026-179
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/JLSEC-2026-179
Type: osv

## Affected
- Julia: `MongoC_jll` — affected >=0 <1.25.1+0

## Details
When calling `bson_utf8_validate` on some inputs a loop with an exit condition that cannot be reached may occur, i.e. an infinite loop. This issue affects All MongoDB C Driver versions prior to versions 1.25.0.

## References
- https://jira.mongodb.org/browse/CDRIVER-4747
- https://lists.debian.org/debian-lts-announce/2025/05/msg00012.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00027.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7GUVOAFZFSYTNBF6R7H4XJM5DHWBRQ6P/
