# [M] Default installation of `synthetic-monitoring-agent` exposes sensitive information

## Summary
Severity: Medium
Advisory: GHSA-9j4f-f249-q5w8
CVE: CVE-2022-46156
CWE: CWE-489, CWE-749
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-09-06
Source: https://github.com/advisories/GHSA-9j4f-f249-q5w8
Type: github-advisory

## Affected
- Go: `github.com/grafana/synthetic-monitoring-agent/cmd/synthetic-monitoring-agent` — affected >=0 <0.12.0
- Go: `github.com/grafana/synthetic-monitoring-agent` — affected >=0 <0.12.0

## Details
### Impact

Users running the Synthetic Monitoring agent in their local network are impacted. The authentication token used to communicate with the Synthetic Monitoring API is exposed thru a debugging endpoint. This token can be used to retrieve the Synthetic Monitoring checks created by the user and assigned to the agent identified with that token. The Synthetic Monitoring API will reject connections from already-connected agents, so access to the token does not guarantee access to the checks.

### Patches

Fixed version is v0.12.0

Users are advised to rotate the agent tokens.

After upgrading to version v0.12.0 or later, it's recommended that user's of distribution packages (e.g. Debian or RedHat and their derivatives) review the configuration stored in `/etc/synthetic-monitoring/synthetic-monitoring-agent.conf`, specifically the `API_TOKEN` variable which has been renamed to `SM_AGENT_API_TOKEN`.

### Workarounds

With all previous versions, it's recommended that users review the agent settings and set the HTTP listening address in a manner that limits the exposure, for example, localhost or a non-routed network, by using the command line parameter `-listen-address`, e.g. `-listen-address localhost:4050`.

### References

The following changes have been made to address this issue:

- [Disable debug endpoint by default](https://github.com/grafana/synthetic-monitoring-agent/pull/373)
- [Allow retrieving the token from the environment](https://github.com/grafana/synthetic-monitoring-agent/pull/374)
- [Default to listening on localhost](https://github.com/grafana/synthetic-monitoring-agent/pull/375)

### For more information

If you have any questions or comments about this advisory:
* You can use the [Synthetic Monitoring Agent discussions](https://github.com/grafana/synthetic-monitoring-agent/discussions).
* Issues should be reported in the [Synthetic Monitoring Agent issues](https://github.com/grafana/synthetic-monitoring-agent/issues).
* Email us at [security@grafana.com](mailto:security@grafana.com).

## References
- https://github.com/grafana/synthetic-monitoring-agent/security/advisories/GHSA-9j4f-f249-q5w8
- https://nvd.nist.gov/vuln/detail/CVE-2022-46156
- https://github.com/grafana/synthetic-monitoring-agent/pull/373
- https://github.com/grafana/synthetic-monitoring-agent/pull/374
- https://github.com/grafana/synthetic-monitoring-agent/pull/375
- https://github.com/grafana/synthetic-monitoring-agent/commit/d8dc7f9c1c641881cbcf0a09e178b90ebf0f0228
- https://github.com/grafana/synthetic-monitoring-agent
- https://github.com/grafana/synthetic-monitoring-agent/releases/tag/v0.12.0
- https://pkg.go.dev/vuln/GO-2022-1132
