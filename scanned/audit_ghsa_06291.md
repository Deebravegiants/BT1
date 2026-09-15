# [H] Fleet: SQL injection in Okta conditional access endpoint allows host-controlled compromise of the Fleet database

## Summary
Severity: High
Advisory: GHSA-7q96-f8xw-jv5j
CVE: CVE-2026-54245
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-7q96-f8xw-jv5j
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet` — affected >=0 <4.86.2

## Details
### Summary

A SQL injection vulnerability in Fleet's Okta conditional access integration could allow an attacker who controls a single enrolled host to read or modify arbitrary data in the Fleet database, including stored session tokens. Disclosed session tokens may be replayed to act as a global administrator, which on a managed fleet leads to remote code execution on enrolled hosts.

### Impact

When Fleet Premium with Okta conditional access is configured, an unauthenticated request path that supports the conditional access integration uses a host-supplied value in a database query without proper parameterization. Because the value is reported by the host's own agent and stored verbatim, any party that controls one enrolled host (the lowest-privilege role in the product) can influence the query.

Successful exploitation could allow:

- Disclosure of arbitrary database contents, including credentials and session tokens.
- Replay of disclosed session tokens to gain global administrator access.
- Subsequent actions available to a global administrator, including running scripts on enrolled hosts.

This issue requires Fleet Premium with the Okta conditional access integration enabled. It does not affect instances where Okta conditional access is not configured.

### Workarounds

If an immediate upgrade is not possible, disable the Okta conditional access integration until the patched version is deployed.

### For more information

If you have any questions or comments about this advisory:

Email us at [security@fleetdm.com](mailto:security@fleetdm.com)

Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits

We thank @fuzzztf for responsibly disclosing this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-7q96-f8xw-jv5j
- https://github.com/fleetdm/fleet
- https://github.com/fleetdm/fleet/releases/tag/fleet-v4.86.2
