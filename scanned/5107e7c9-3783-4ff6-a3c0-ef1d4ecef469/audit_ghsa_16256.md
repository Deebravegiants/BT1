# [H] `@backstage/backend-common` vulnerable to path traversal through symlinks

## Summary
Severity: High
Advisory: GHSA-2fc9-xpp8-2g9h
CVE: CVE-2024-26150
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-23
Source: https://github.com/advisories/GHSA-2fc9-xpp8-2g9h
Type: github-advisory

## Affected
- npm: `@backstage/backend-common` — affected >=0.21.0 <0.21.1
- npm: `@backstage/backend-common` — affected >=0 <0.19.10
- npm: `@backstage/backend-common` — affected >=0.20.0 <0.20.2

## Details
### Impact

Paths checks with the `resolveSafeChildPath` utility were not exhaustive enough, leading to risk of path traversal vulnerabilities if symlinks can be injected by attackers.

### Patches
Patched in `@backstage/backend-common` version `0.21.1`.
Patched in `@backstage/backend-common` version `0.20.2`.
Patched in `@backstage/backend-common` version `0.19.10`.


### For more information
If you have any questions or comments about this advisory:

- Open an issue in the [Backstage repository](https://github.com/backstage/backstage)
- Visit our Discord, linked to in [Backstage README](https://github.com/backstage/backstage)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-2fc9-xpp8-2g9h
- https://nvd.nist.gov/vuln/detail/CVE-2024-26150
- https://github.com/backstage/backstage/commit/1ad2b1b61ebb430051f7d804b0cc7ebfe7922b6f
- https://github.com/backstage/backstage/commit/78f892b3a84d63de2ba167928f171154c447b717
- https://github.com/backstage/backstage/commit/edf65d7d31e027599c2415f597d085ee84807871
- https://github.com/backstage/backstage
