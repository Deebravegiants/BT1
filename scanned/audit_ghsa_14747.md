# [M] Synapse Matrix has a partial room state leak via Sliding Sync

## Summary
Severity: Medium
Advisory: GHSA-56w4-5538-8v8h
CVE: CVE-2024-53867
CWE: CWE-497
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-12-03
Source: https://github.com/advisories/GHSA-56w4-5538-8v8h
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=1.113.0rc1 <1.120.1

## Details
### Impact
The Sliding Sync feature on Synapse versions between 1.113.0rc1 and 1.120.0 can leak partial room state changes to users no longer in a room. Non-state events, like messages, are unaffected.

### Patches
Synapse version 1.120.1 fixes the problem.

### Workarounds
Disable Sliding Sync.

### References
https://github.com/matrix-org/matrix-spec-proposals/pull/4186
https://github.com/element-hq/synapse/blob/d80cd57c54427687afcb48740d99219c88a0fff1/synapse/config/experimental.py#L341-L344

### For more information

If you have any questions or comments about this advisory, please email us at [security at element.io](mailto:security@element.io).

## References
- https://github.com/element-hq/synapse/security/advisories/GHSA-56w4-5538-8v8h
- https://nvd.nist.gov/vuln/detail/CVE-2024-53867
- https://github.com/matrix-org/matrix-spec-proposals/pull/4186
- https://github.com/element-hq/synapse
