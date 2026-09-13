# [H] BIT-sqlite-2022-46908

## Summary
Severity: High
Advisory: BIT-sqlite-2022-46908
Aliases: CVE-2022-46908
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-sqlite-2022-46908
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=3.37.0 <3.40.1

## Details
SQLite through 3.40.0, when relying on --safe for execution of an untrusted CLI script, does not properly implement the azProhibitedFunctions protection mechanism, and instead allows UDF functions such as WRITEFILE.

## References
- https://news.ycombinator.com/item?id=33948588
- https://security.gentoo.org/glsa/202311-03
- https://security.netapp.com/advisory/ntap-20230203-0005/
- https://sqlite.org/forum/forumpost/07beac8056151b2f
- https://sqlite.org/src/info/cefc032473ac5ad2
- https://nvd.nist.gov/vuln/detail/CVE-2022-46908
