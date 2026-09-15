# [M] Fleet: Unauthenticated Android device disenrollment vulnerability via Pub/Sub endpoint 

## Summary
Severity: Medium
Advisory: GHSA-9pm7-6g36-6j78
CVE: CVE-2026-24004
CWE: CWE-306, CWE-862
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:N/SA:L (CVSS_V4)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-9pm7-6g36-6j78
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.80.1

## Details
### Summary

A vulnerability in Fleet’s Android MDM Pub/Sub handling could allow unauthenticated requests to trigger device unenrollment events. This may result in unauthorized removal of individual Android devices from Fleet management.

### Impact

If Android MDM is enabled, an attacker could send a crafted request to the Android Pub/Sub endpoint to unenroll a targeted Android device from Fleet without authentication.

This issue does not grant access to Fleet, allow execution of commands, or provide visibility into device data. Impact is limited to disruption of Android device management for the affected device.

### Workarounds

If an immediate upgrade is not possible, affected Fleet users should temporarily disable Android MDM.

### For more information

If there any questions or comments about this advisory:

Email Fleet at [security@fleetdm.com](mailto:security@fleetdm.com)
Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits

Fleet thanks @secfox-ai for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-9pm7-6g36-6j78
- https://nvd.nist.gov/vuln/detail/CVE-2026-24004
- https://github.com/fleetdm/fleet/commit/24dd2257ae7127680a2f6cd1a4eee58a9c95dd34
- https://github.com/fleetdm/fleet
