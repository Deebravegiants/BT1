# [H] BIT-sqlite-2025-70873

## Summary
Severity: High
Advisory: BIT-sqlite-2025-70873
Aliases: CVE-2025-70873
Ecosystem: Bitnami
Published: 2026-04-18
Source: https://osv.dev/vulnerability/BIT-sqlite-2025-70873
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=0 <3.51.1

## Details
An information disclosure issue in the zipfileInflate function in the zipfile extension in SQLite v3.51.1 and earlier allows attackers to obtain heap memory via supplying a crafted ZIP file.

## References
- https://gist.github.com/cnwangjihe/f496393f30f5ecec5b18c8f5ab072054
- https://nvd.nist.gov/vuln/detail/CVE-2025-70873
- https://sqlite.org/forum/forumpost/761eac3c82
- https://sqlite.org/src/info/3d459f1fb1bd1b5e
