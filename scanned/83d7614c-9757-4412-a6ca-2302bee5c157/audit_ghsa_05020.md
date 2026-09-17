# [M] Fleet has observer-level enrollment secret extraction via ORDER BY oracle on labels host-listing endpoint

## Summary
Severity: Medium
Advisory: GHSA-vxm7-9x8v-8gm4
CVE: CVE-2026-46370
CWE: CWE-200, CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-vxm7-9x8v-8gm4
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.84.2

## Details
### Summary

A vulnerability in Fleet's labels host-listing endpoint allowed authenticated users with the lowest-privilege Observer role to extract host enrollment secrets (`node_key`, `orbit_node_key`) through a cursor-based binary search oracle. The endpoint accepted a user-supplied `order_key` parameter that was not validated against a column allowlist, permitting sort order to be driven by sensitive columns in a joined table.

### Impact

The `GET /api/v1/fleet/labels/{id}/hosts` endpoint constructs its query using a deprecated helper that did not restrict which columns could appear in the `ORDER BY` clause. An attacker with Global Observer or Team Observer credentials could supply a sensitive column name (for example, `h.node_key`) as `order_key` and combine it with the cursor-based `after` parameter to binary-search the values of those columns one character at a time. The targeted values never appeared in the response body, but the presence or absence of results revealed each character.

The `node_key` and `orbit_node_key` values are the long-lived shared secrets used by osquery and Orbit agents to authenticate to the Fleet server. An attacker who extracted these keys could:

- Impersonate enrolled hosts to Fleet's osquery and Orbit endpoints
- Submit fabricated query results and host inventory data
- Retrieve pending scripts and MDM commands queued for the host
- Poison compliance and policy results across the Fleet deployment

Exploitation required authenticated Observer access. Fleet deployments that restrict Observer roles to fully trusted users were at lower practical risk, but the secrets exposed are high-value and long-lived.

### Patches

- v4.85.0

### Workarounds

If an immediate upgrade is not possible, administrators should:

- Restrict the Observer role to fully trusted users until the patch is applied
- Rotate `node_key` and `orbit_node_key` for any host suspected of exposure by re-enrolling the affected hosts

### For more information

If there are any questions or comments about this advisory:

Email Fleet at [security@fleetdm.com](mailto:security@fleetdm.com)
Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits

Fleet thanks the Security Team at Palantir Technologies for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-vxm7-9x8v-8gm4
- https://github.com/fleetdm/fleet
