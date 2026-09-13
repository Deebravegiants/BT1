# [M] Fleet vulnerable to OS command injection in software packages

## Summary
Severity: Medium
Advisory: GHSA-9vcr-g537-3w5v
CVE: CVE-2026-26191
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-9vcr-g537-3w5v
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.81.1

## Details
### Summary

A vulnerability in Fleet's software installer pipeline could allow a crafted software package to execute arbitrary commands as root (macOS/Linux) or SYSTEM (Windows) on managed endpoints when an uninstall is triggered.

### Impact

When a software package (.pkg, .deb, .rpm, .exe, or .msi) is uploaded to Fleet, metadata is extracted from the package binary and used to generate uninstall scripts. In affected versions, this metadata is not properly sanitized before being included in the generated scripts. A specially crafted package containing malicious values in its metadata fields could result in unintended command execution when the uninstall script runs on managed endpoints.

### Workarounds

If an immediate upgrade is not possible, administrators should avoid uploading software packages obtained from untrusted or unverified sources. Additionally, administrators can manually inspect and edit auto-generated uninstall scripts before deployment.

### For more information

If you have any questions or comments about this advisory:

Email us at [[security@fleetdm.com](mailto:security@fleetdm.com)](mailto:security@fleetdm.com)

Join #fleet in [[osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits

We thank @secfox-ai for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-9vcr-g537-3w5v
- https://nvd.nist.gov/vuln/detail/CVE-2026-26191
- https://github.com/fleetdm/fleet
- https://github.com/fleetdm/fleet/releases/tag/fleet-v4.81.1
