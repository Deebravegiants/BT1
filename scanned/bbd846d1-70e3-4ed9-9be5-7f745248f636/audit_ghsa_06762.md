# [H] TensorZero Gateway: Arbitrary file read and SSRF in internal object storage endpoint

## Summary
Severity: High
Advisory: GHSA-824w-x939-6cmc
CVE: CVE-2026-54457
CWE: CWE-552, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-824w-x939-6cmc
Type: github-advisory

## Affected
- PyPI: `tensorzero` — affected >=0 <2026.6.0

## Details
### Impact

The `/internal/object_storage` endpoint accepts a caller-supplied JSON `storage_path` parameter that dynamically overrides the TensorZero `[object_storage]` configuration.

By abusing the `filesystem` storage type, a caller can read arbitrary files from the gateway filesystem, including files that may contain sensitive credentials. Similarly, by abusing the `s3_compatible` storage type, the caller can coerce the gateway into making outbound object storage requests to attacker-chosen internal/cloud-metadata endpoints.

This vulnerability only applies when the gateway can be accessed by untrusted callers. If a developer's TensorZero deployment has authentication enabled, only authenticated callers can exploit this vulnerability. If a developer's deployment has authentication disabled, any caller can exploit this vulnerability.

### Remediation

The vulnerability has been patched in version `2026.6.0`. See PR #7527.

### Workarounds

If developers are unable to upgrade a gateway that is exposed to untrusted callers, please block external access to the `/internal/object_storage` endpoint.

## References
- https://github.com/tensorzero/tensorzero/security/advisories/GHSA-824w-x939-6cmc
- https://github.com/tensorzero/tensorzero/commit/0abbc838bae3394fe7491dad7009670d4e3b6cf8
- https://github.com/tensorzero/tensorzero
- https://github.com/tensorzero/tensorzero/releases/tag/2026.6.0
