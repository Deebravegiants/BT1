# [M] Zitadel exposing internal database user name and host information

## Summary
Severity: Medium
Advisory: GHSA-q5qj-x2h5-3945
CVE: CVE-2024-32967
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-01
Source: https://github.com/advisories/GHSA-q5qj-x2h5-3945
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=2.50.0 <2.50.3
- Go: `github.com/zitadel/zitadel` — affected >=2.49.0 <2.49.5
- Go: `github.com/zitadel/zitadel` — affected >=2.48.0 <2.48.5
- Go: `github.com/zitadel/zitadel` — affected >=2.47.0 <2.47.10
- Go: `github.com/zitadel/zitadel` — affected >=0 <2.45.7

## Details
### Impact

In case ZITADEL could not connect to the database, connection information including db name, username and db host name could be returned to the user.

### Patches

2.x versions are fixed on >= [2.50.3](https://github.com/zitadel/zitadel/releases/tag/v2.50.3)
2.49.x versions are fixed on >= [2.49.5](https://github.com/zitadel/zitadel/releases/tag/v2.49.5)
2.48.x versions are fixed on >= [2.48.5](https://github.com/zitadel/zitadel/releases/tag/v2.48.5)
2.47.x versions are fixed on >= [2.47.10](https://github.com/zitadel/zitadel/releases/tag/v2.47.10)
2.46.x versions are fixed on >= [2.46.7](https://github.com/zitadel/zitadel/releases/tag/v2.46.7)
2.45.x versions are fixed on >= [2.45.7](https://github.com/zitadel/zitadel/releases/tag/v2.45.7)

### Workarounds

There is no workaround since a patch is already available.

### Questions

If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-q5qj-x2h5-3945
- https://nvd.nist.gov/vuln/detail/CVE-2024-32967
- https://github.com/zitadel/zitadel/commit/b918603b576d156a08b90917c14c2d019c82ffc6
- https://github.com/zitadel/zitadel
- https://github.com/zitadel/zitadel/releases/tag/v2.45.7
- https://github.com/zitadel/zitadel/releases/tag/v2.46.7
- https://github.com/zitadel/zitadel/releases/tag/v2.47.10
- https://github.com/zitadel/zitadel/releases/tag/v2.48.5
- https://github.com/zitadel/zitadel/releases/tag/v2.49.5
- https://github.com/zitadel/zitadel/releases/tag/v2.50.3
