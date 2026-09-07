# [M] Fleet has an SQL Injection vulnerability via backtick escape in ORDER BY parameter

## Summary
Severity: Medium
Advisory: GHSA-49xw-vfc4-7p43
CVE: CVE-2026-26186
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-49xw-vfc4-7p43
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.80.1

## Details
### Summary

A SQL Injection vulnerability in Fleet’s software versions API allowed authenticated users to inject arbitrary SQL expressions via the `order_key` query parameter. Due to unsafe use of `goqu.I()` when constructing the `ORDER BY` clause, specially crafted input could escape identifier quoting and be interpreted as executable SQL.

### Impact

An authenticated attacker with access to the affected endpoint could inject SQL expressions into the underlying MySQL query. Although the injection occurs in an `ORDER BY` context, it is sufficient to enable blind SQL injection techniques that can disclose database information through conditional expressions that affect result ordering. Crafted expressions may also cause excessive computation or query failures, potentially leading to degraded performance or denial of service.

No direct evidence of reliable data modification or stacked query execution was demonstrated.

### Workarounds

If an immediate upgrade is not possible, users should restrict access to the affected endpoint to trusted roles only and ensure that any user-supplied sort or column parameters are strictly allow-listed at the application or proxy layer.

### For more information

If there are any questions or comments about this advisory:

Email fleet at [security@fleetdm.com](mailto:security@fleetdm.com)  
Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits

We thank @fuzzztf for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-49xw-vfc4-7p43
- https://nvd.nist.gov/vuln/detail/CVE-2026-26186
- https://github.com/fleetdm/fleet
- https://github.com/fleetdm/fleet/releases/tag/fleet-v4.80.1
