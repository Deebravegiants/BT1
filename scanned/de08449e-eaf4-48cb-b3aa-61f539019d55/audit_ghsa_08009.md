# [M] Fleet: Device lock PIN can be predicted if lock time is known

## Summary
Severity: Medium
Advisory: GHSA-ppwx-5jq7-px2w
CVE: CVE-2026-23999
CWE: CWE-330
Ecosystem: Go
CVSS: CVSS:4.0/AV:P/AC:H/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-ppwx-5jq7-px2w
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.80.1

## Details
### Summary

Fleet generated device lock and wipe PINs using a predictable algorithm based solely on the current Unix timestamp. Because no secret key or additional entropy was used, the resulting PIN could potentially be derived if the approximate time the device was locked is known.

### Impact

Fleet’s device lock and wipe commands generate a 6-digit PIN that is displayed to administrators for unlocking a device. In affected versions, this PIN was deterministically derived from the current timestamp.

An attacker with physical possession of a locked device and knowledge of the approximate time the lock command was issued could theoretically predict the correct PIN within a limited search window.

However, successful exploitation is constrained by multiple factors:
- Physical access to the device is required.
- The approximate lock time must be known.
- The operating system enforces rate limiting on PIN entry attempts.
- Attempts would need to be spread over multiple days.
- Device wipe operations would typically complete before sufficient attempts could be made.

As a result, this issue does not allow remote exploitation, fleet-wide compromise, or bypass of Fleet authentication controls.

### Workarounds

There are no known workarounds for this issue. Customers should upgrade to a patched version.

### For more information

If there are any questions or comments about this advisory:

Email Fleet at [security@fleetdm.com](mailto:security@fleetdm.com)
Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits

Fleet thanks @secfox-ai for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-ppwx-5jq7-px2w
- https://nvd.nist.gov/vuln/detail/CVE-2026-23999
- https://github.com/fleetdm/fleet/commit/05ca0693621e6671fb95dfc5437b9f9ee6dd7047
- https://github.com/fleetdm/fleet
