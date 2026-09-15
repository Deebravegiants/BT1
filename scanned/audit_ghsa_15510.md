# [H] ZITADEL's User Grant Deactivation not Working

## Summary
Severity: High
Advisory: GHSA-2w5j-qfvw-2hf5
CVE: CVE-2024-46999
CWE: CWE-269, CWE-672
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-09-19
Source: https://github.com/advisories/GHSA-2w5j-qfvw-2hf5
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel/v2` — affected >=2.62.0 <2.62.1
- Go: `github.com/zitadel/zitadel/v2` — affected >=2.61.0 <2.61.1
- Go: `github.com/zitadel/zitadel/v2` — affected >=2.60.0 <2.60.2
- Go: `github.com/zitadel/zitadel/v2` — affected >=2.59.0 <2.59.3
- Go: `github.com/zitadel/zitadel/v2` — affected >=2.58.0 <2.58.5
- Go: `github.com/zitadel/zitadel/v2` — affected >=2.57.0 <2.57.5
- Go: `github.com/zitadel/zitadel/v2` — affected >=2.56.0 <2.56.6
- Go: `github.com/zitadel/zitadel/v2` — affected >=2.55.0 <2.55.8
- Go: `github.com/zitadel/zitadel/v2` — affected >=0 <2.54.10

## Details
### Impact

ZITADEL's user grants deactivation mechanism did not work correctly. Deactivated user grants were still provided in token, which could lead to unauthorized access to applications and resources.
Additionally, the management and auth API always returned the state as active or did not provide any information about the state.

### Patches

2.x versions are fixed on >= [2.62.1](https://github.com/zitadel/zitadel/releases/tag/v2.62.1)
2.61.x versions are fixed on >= [2.61.1](https://github.com/zitadel/zitadel/releases/tag/v2.61.1)
2.60.x versions are fixed on >= [2.60.2](https://github.com/zitadel/zitadel/releases/tag/v2.60.2)
2.59.x versions are fixed on >= [2.59.3](https://github.com/zitadel/zitadel/releases/tag/v2.59.3)
2.58.x versions are fixed on >= [2.58.5](https://github.com/zitadel/zitadel/releases/tag/v2.58.5)
2.57.x versions are fixed on >= [2.57.5](https://github.com/zitadel/zitadel/releases/tag/v2.57.5)
2.56.x versions are fixed on >= [2.56.6](https://github.com/zitadel/zitadel/releases/tag/v2.56.6)
2.55.x versions are fixed on >= [2.55.8](https://github.com/zitadel/zitadel/releases/tag/v2.55.8)
2.54.x versions are fixed on >= [2.54.10](https://github.com/zitadel/zitadel/releases/tag/v2.54.10)

### Workarounds

Unpatched versions can explicitly remove the user grants to make sure the user does not get access anymore.

### Questions

If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-2w5j-qfvw-2hf5
- https://nvd.nist.gov/vuln/detail/CVE-2024-46999
- https://github.com/zitadel/zitadel
