# [H] Fleet: Sensitive Google Calendar credentials disclosed to low-privileged users

## Summary
Severity: High
Advisory: GHSA-2v6m-6xw3-6467
CVE: CVE-2026-27465
CWE: CWE-200, CWE-201
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-2v6m-6xw3-6467
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.80.1

## Details
### Summary

A vulnerability in Fleet’s configuration API could expose Google Calendar service account credentials to authenticated users with low-privilege roles. This may allow unauthorized access to Google Calendar resources associated with the service account.

### Impact

Fleet returns configuration data through an API endpoint that is accessible to authenticated users, including those with the lowest-privilege “Observer” role. In affected versions, Google Calendar service account credentials were not properly obfuscated before being returned.

As a result, a low-privilege user could retrieve the service account’s private key material. Depending on how the Google Calendar integration is configured, this could allow unauthorized access to calendar data or other Google Workspace resources associated with the service account.

This issue does not allow escalation of privileges within Fleet or access to device management functionality.

### Patches

- v4.80.1

### Workarounds

If an immediate upgrade is not possible, administrators should remove the Google Calendar integration from Fleet and rotate the affected Google service account credentials.

### For more information

If there are any questions or comments about this advisory:

Email Fleet at [security@fleetdm.com](mailto:security@fleetdm.com)  
Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits

Fleet thanks @secfox-ai for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-2v6m-6xw3-6467
- https://nvd.nist.gov/vuln/detail/CVE-2026-27465
- https://github.com/fleetdm/fleet/commit/23fc6804efe785f806f769d6be1f5f05b2e13ec2
- https://github.com/fleetdm/fleet
