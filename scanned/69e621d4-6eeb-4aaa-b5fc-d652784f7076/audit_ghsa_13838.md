# [H] api-platform/core's secured properties may be accessible within collections

## Summary
Severity: High
Advisory: GHSA-vr2x-7687-h6qv
CVE: CVE-2023-25575
CWE: CWE-842, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-02-28
Source: https://github.com/advisories/GHSA-vr2x-7687-h6qv
Type: github-advisory

## Affected
- Packagist: `api-platform/core` — affected >=3.0.0 <3.0.12
- Packagist: `api-platform/core` — affected >=3.1.0 <3.1.3
- Packagist: `api-platform/core` — affected >=2.6.0 <2.7.10

## Details
### Impact

Resource properties secured with the `security` option of the `ApiPlatform\Metadata\ApiProperty` attribute can be disclosed to unauthorized users. The problem affects most serialization formats, including raw JSON, which is enabled by default when installing API Platform. Custom serialization formats may also be impacted. Only collection endpoints are affected by the issue, item endpoints are not. The JSON-LD format is not affected by the issue.

The result of the security rule is only executed for the first item of the collection. The result of the rule is then cached and reused for the next items. This bug can leak data to unauthorized users when the rule depends on the value of a property of the item. This bug can also hide properties that should be displayed to authorized users.

### Patches

This issue impacts the 2.7, 3.0 and 3.1 branches. Upgrade to v2.7.10, v3.0.12 or v3.1.3.

### Workarounds

Replace the `cache_key` of the context array of the Serializer inside a custom normalizer that works on objects if the security option of the `ApiPlatform\Metadata\ApiProperty` attribute is used.

## References
- https://github.com/api-platform/core/security/advisories/GHSA-vr2x-7687-h6qv
- https://nvd.nist.gov/vuln/detail/CVE-2023-25575
- https://github.com/api-platform/core/commit/5723d68369722feefeb11e42528d9580db5dd0fb
- https://github.com/FriendsOfPHP/security-advisories/blob/master/api-platform/core/CVE-2023-25575.yaml
- https://github.com/api-platform/core
- https://github.com/api-platform/core/releases/tag/v2.7.10
- https://github.com/api-platform/core/releases/tag/v3.0.12
- https://github.com/api-platform/core/releases/tag/v3.1.3
