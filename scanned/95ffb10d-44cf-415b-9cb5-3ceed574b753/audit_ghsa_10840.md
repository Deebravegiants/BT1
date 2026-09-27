# [M] A Fleet team maintainer can transfer hosts from any team via missing source team authorization

## Summary
Severity: Medium
Advisory: GHSA-m2h6-4xpq-qw3m
CVE: CVE-2026-29180
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-m2h6-4xpq-qw3m
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.81.1

## Details
### Summary

A broken access control vulnerability in Fleet's host transfer API allows a team maintainer to transfer hosts from any team into their own team, bypassing team isolation boundaries. Once transferred, the attacker gains full control over the stolen hosts, including the ability to execute scripts with root privileges.

### Impact

The host transfer endpoints verify that the caller has write permission to the destination team but do not check whether the caller has any permission over the source team of the hosts being transferred.

Once hosts are transferred, the attacker's team MDM configuration is automatically applied to the stolen devices, and the attacker can execute scripts on them with root privileges. In multi-tenant Fleet deployments where teams represent business units, departments, or customers, this breaks all team isolation guarantees. A bulk transfer variant allows stealing all matching hosts fleet-wide in a single request.

Exploitation requires authentication as a team maintainer or team admin.

### Workarounds

There is no workaround for this issue short of upgrading to a patched version. Organizations concerned about exploitation should audit host transfer activity in their Fleet logs for any unexpected team reassignments.

### For more information

If there are any questions or comments about this advisory:

Email Fleet at [security@fleetdm.com](mailto:security@fleetdm.com)
Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits

Fleet thanks @secfox-ai for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-m2h6-4xpq-qw3m
- https://nvd.nist.gov/vuln/detail/CVE-2026-29180
- https://github.com/fleetdm/fleet
- https://github.com/fleetdm/fleet/releases/tag/fleet-v4.81.1
