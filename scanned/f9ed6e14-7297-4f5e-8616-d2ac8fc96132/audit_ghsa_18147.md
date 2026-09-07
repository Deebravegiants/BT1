# [M] Infrahub: Deleted and expired API tokens can still authenticate

## Summary
Severity: Medium
Advisory: GHSA-v2p7-4pv4-3wwh
CVE: CVE-2025-59036
CWE: CWE-298
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-09-10
Source: https://github.com/advisories/GHSA-v2p7-4pv4-3wwh
Type: github-advisory

## Affected
- PyPI: `infrahub-server` — affected >=0 <1.3.9
- PyPI: `infrahub-server` — affected >=1.4.0 <1.4.5

## Details
### Impact
A bug in the authentication logic will cause API tokens that were deleted and/or expired to be considered valid. This means that any API token that is associated with an active user account can authenticate successfully.

### Patches
This issue is fixed in versions `1.3.9` and `1.4.5`

### Workarounds
Users can delete or deactivate the account associated with a deleted API token to prevent that token from authenticating.

## References
- https://github.com/opsmill/infrahub/security/advisories/GHSA-v2p7-4pv4-3wwh
- https://nvd.nist.gov/vuln/detail/CVE-2025-59036
- https://github.com/opsmill/infrahub/commit/215185f217e2f754f7c0a0aa4b77e11079a063a1
- https://github.com/opsmill/infrahub/commit/61b49a4a9e988f10c3a44f0e86ef97f344a1e228
- https://github.com/opsmill/infrahub
- https://github.com/opsmill/infrahub/releases/tag/infrahub-v1.3.9
- https://github.com/opsmill/infrahub/releases/tag/infrahub-v1.4.5
