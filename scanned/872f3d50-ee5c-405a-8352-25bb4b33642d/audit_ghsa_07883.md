# [M] Fleet: Authorization Bypass in certificate template batch deletion for team administrators

## Summary
Severity: Medium
Advisory: GHSA-5jvp-m9h4-253h
CVE: CVE-2026-25963
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-5jvp-m9h4-253h
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.80.1

## Details
### Summary

A broken authorization check in Fleet’s certificate template deletion API could allow a team administrator to delete certificate templates belonging to other teams within the same Fleet instance.

### Impact

Fleet supports certificate templates that are scoped to individual teams. In affected versions, the batch deletion endpoint validated authorization using a user-supplied team identifier but did not verify that the certificate template IDs being deleted actually belonged to that team.

As a result, a team administrator could delete certificate templates associated with other teams, potentially disrupting certificate-based workflows such as device enrollment, Wi-Fi authentication, VPN access, or other certificate-dependent configurations for the affected teams.

This issue does not allow privilege escalation, access to sensitive data, or compromise of Fleet’s control plane. Impact is limited to integrity and availability of certificate templates across teams.

### Patches

- v4.80.1

### Workarounds

If an immediate upgrade is not possible, administrators should restrict access to certificate template management to trusted users and avoid delegating team administrator permissions where not strictly required.

### For more information

If there are any questions or comments about this advisory:

Email Fleet at [security@fleetdm.com](mailto:security@fleetdm.com)  
Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits

Fleet thanks @secfox-ai for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-5jvp-m9h4-253h
- https://nvd.nist.gov/vuln/detail/CVE-2026-25963
- https://github.com/fleetdm/fleet/commit/d27d0362db390fe835e3b5328525f25018df0fb7
- https://github.com/fleetdm/fleet
