# [H] `libsqlite3-sys` via C SQLite improperly validates array index

## Summary
Severity: High
Advisory: GHSA-jw36-hf63-69r9
CVE: CVE-2022-35737
CWE: CWE-129
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-04
Source: https://github.com/advisories/GHSA-jw36-hf63-69r9
Type: github-advisory

## Affected
- crates.io: `libsqlite3-sys` — affected >=0 <0.25.1

## Details
SQLite 1.0.12 through 3.39.x before 3.39.2 sometimes allows an array-bounds overflow if billions of bytes are used in a string argument to a C API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35737
- https://blog.trailofbits.com/2022/10/25/sqlite-vulnerability-july-2022-library-api
- https://github.com/rusqlite/rusqlite
- https://kb.cert.org/vuls/id/720344
- https://rustsec.org/advisories/RUSTSEC-2022-0090.html
- https://security.gentoo.org/glsa/202210-40
- https://security.netapp.com/advisory/ntap-20220915-0009
- https://sqlite.org/releaselog/3_39_2.html
- https://www.sqlite.org/cves.html
