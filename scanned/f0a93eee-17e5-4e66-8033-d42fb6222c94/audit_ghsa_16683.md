# [H] Npgsql vulnerable to SQL Injection via Protocol Message Size Overflow

## Summary
Severity: High
Advisory: GHSA-x9vc-6hfv-hg8c
CVE: CVE-2024-32655
CWE: CWE-190, CWE-89
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-09
Source: https://github.com/advisories/GHSA-x9vc-6hfv-hg8c
Type: github-advisory

## Affected
- NuGet: `Npgsql` — affected >=8.0.0 <8.0.3
- NuGet: `Npgsql` — affected >=0 <4.0.14
- NuGet: `Npgsql` — affected >=4.1.0 <4.1.13
- NuGet: `Npgsql` — affected >=5.0.0 <5.0.18
- NuGet: `Npgsql` — affected >=6.0.0 <6.0.11
- NuGet: `Npgsql` — affected >=7.0.0 <7.0.7

## Details
### Summary
The `WriteBind()` method in `src/Npgsql/Internal/NpgsqlConnector.FrontendMessages.cs` uses `int` variables to store the message length and the sum of parameter lengths. Both variables overflow when the sum of parameter lengths becomes too large.

This causes Npgsql to write a message size that is too small when constructing a Postgres protocol message to send it over the network to the database. When parsing the message, the database will only read a small number of bytes and treat any following bytes as new messages while they belong to the old message.

Attackers can abuse this to inject arbitrary Postgres protocol messages into the connection, leading to the execution of arbitrary SQL statements on the application's behalf.

### Impact
Attackers can issue arbitrary SQL statements to the database on behalf of the application. The final impact depends on the application that uses Npgsql, the data it stores in Postgres, etc.

## References
- https://github.com/npgsql/npgsql/security/advisories/GHSA-x9vc-6hfv-hg8c
- https://nvd.nist.gov/vuln/detail/CVE-2024-32655
- https://github.com/npgsql/npgsql/commit/091655eed0c84e502ab424950c930339d17c1928
- https://github.com/npgsql/npgsql/commit/3183efb2bdcca159c8c2e22af57e18ea8f853cf0
- https://github.com/npgsql/npgsql/commit/67acbe027e28477ac2199e15cfb554bb2ffaf169
- https://github.com/npgsql/npgsql/commit/703d9af8fa48dfe8c0180e36edb8278f34342d7b
- https://github.com/npgsql/npgsql/commit/a22a42d8141d7a3528f43c02c095a409507cf1af
- https://github.com/npgsql/npgsql/commit/e34e2ba8042e666d9af54a1b255fba4d5b11df56
- https://github.com/npgsql/npgsql/commit/f7e7ead0702d776a8f551f5786c4cac2d65c4bc6
- https://www.youtube.com/watch?v=Tfg1B8u1yvE
- https://github.com/npgsql/npgsql/releases/tag/v8.0.3
- https://github.com/npgsql/npgsql/releases/tag/v7.0.7
- https://github.com/npgsql/npgsql/releases/tag/v6.0.11
- https://github.com/npgsql/npgsql/releases/tag/v5.0.18
- https://github.com/npgsql/npgsql/releases/tag/v4.1.13
- https://github.com/npgsql/npgsql/releases/tag/v4.0.14
- https://github.com/npgsql/npgsql/files/14309397/npgsql-protocol-overflow-poc.zip
- https://github.com/npgsql/npgsql/files/14309386/Npgsql.Security.Advisory.pdf
- https://github.com/npgsql/npgsql
