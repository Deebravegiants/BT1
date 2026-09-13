# [H] Server crash when using specific form of SET BIND statement

## Summary
Severity: High
Advisory: CVE-2023-41038
Aliases: GHSA-6fv8-8rwr-9692
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-20
Source: https://osv.dev/vulnerability/CVE-2023-41038
Type: osv

## Details
Firebird is a relational database. Versions 4.0.0 through 4.0.3 and version 5.0 beta1 are vulnerable to a server crash when a user uses a specific form of SET BIND statement. Any non-privileged user with minimum access to a server may type a statement with a long `CHAR` length, which causes the server to crash due to stack corruption. Versions 4.0.4.2981 and 5.0.0.117 contain fixes for this issue. No known workarounds are available.

## References
- https://firebirdsql.org/en/snapshot-builds
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/41xxx/CVE-2023-41038.json
- https://github.com/FirebirdSQL/firebird/security/advisories/GHSA-6fv8-8rwr-9692
- https://nvd.nist.gov/vuln/detail/CVE-2023-41038
