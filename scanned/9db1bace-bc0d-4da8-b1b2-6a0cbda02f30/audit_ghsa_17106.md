# [H] ZITADEL's actions can overload reserved claims

## Summary
Severity: High
Advisory: GHSA-gp8g-f42f-95q2
CVE: CVE-2024-29892
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-03-28
Source: https://github.com/advisories/GHSA-gp8g-f42f-95q2
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=0 <2.42.17
- Go: `github.com/zitadel/zitadel` — affected >=2.43.0 <2.43.11
- Go: `github.com/zitadel/zitadel` — affected >=2.44.0 <2.44.7
- Go: `github.com/zitadel/zitadel` — affected >=2.45.0 <2.45.5
- Go: `github.com/zitadel/zitadel` — affected >=2.46.0 <2.46.5
- Go: `github.com/zitadel/zitadel` — affected >=2.47.0 <2.47.8
- Go: `github.com/zitadel/zitadel` — affected >=2.48.0 <2.48.3

## Details
### Impact
Under certain circumstances an action could set [reserved claims](https://zitadel.com/docs/apis/openidoauth/claims#reserved-claims) managed by ZITADEL.

For example it would be possible to set the claim `urn:zitadel:iam:user:resourceowner:name`

```json
{"urn:zitadel:iam:user:resourceowner:name": "ACME"}
```

if it was not set by ZITADEL itself.

To compensate for this we introduced a protection that does prevent actions from changing claims that start with `urn:zitadel:iam`

### Patches
2.x versions are fixed on >= [2.48.3](https://github.com/zitadel/zitadel/releases/tag/v2.48.3)
2.47.x versions are fixed on >= [2.47.8](https://github.com/zitadel/zitadel/releases/tag/v2.47.8)
2.46.x versions are fixed on >= [2.46.5](https://github.com/zitadel/zitadel/releases/tag/v2.46.5)
2.45.x versions are fixed on >= [2.45.5](https://github.com/zitadel/zitadel/releases/tag/v2.45.5)
2.44.x versions are fixed on >= [2.44.7](https://github.com/zitadel/zitadel/releases/tag/v2.44.7)
2.43.x versions are fixed on >= [2.43.11](https://github.com/zitadel/zitadel/releases/tag/v2.43.11)
2.42.x versions are fixed on >= [2.42.17](https://github.com/zitadel/zitadel/releases/tag/v2.42.17)

### Workarounds
No workaround available since a patch is available

### Credits
Many thanks to @schettn whose disclosure of another topic lead us to find this issue.

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-gp8g-f42f-95q2
- https://nvd.nist.gov/vuln/detail/CVE-2024-29892
- https://github.com/zitadel/zitadel
- https://github.com/zitadel/zitadel/releases/tag/v2.42.17
- https://github.com/zitadel/zitadel/releases/tag/v2.43.11
- https://github.com/zitadel/zitadel/releases/tag/v2.44.7
- https://github.com/zitadel/zitadel/releases/tag/v2.45.5
- https://github.com/zitadel/zitadel/releases/tag/v2.46.5
- https://github.com/zitadel/zitadel/releases/tag/v2.47.8
- https://github.com/zitadel/zitadel/releases/tag/v2.48.3
