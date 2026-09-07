# [H] Fleet has a Windows MDM management endpoint authentication bypass

## Summary
Severity: High
Advisory: GHSA-2rc4-7jc6-qffh
CVE: CVE-2026-23998
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-2rc4-7jc6-qffh
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.81.0

## Details
### Summary

A vulnerability in Fleet’s Windows MDM management endpoint could allow requests to be processed without proper client certificate validation. In certain circumstances, this could allow an attacker to impersonate an enrolled Windows device and retrieve sensitive configuration data.

### Impact

Fleet’s Windows MDM management endpoint relies on mutual TLS (mTLS) client certificates to authenticate enrolled devices. In affected versions, requests that did not present a client certificate could be incorrectly treated as trusted.

As a result, an attacker with prior knowledge of a valid enrolled device identifier could potentially impersonate that device and receive configuration payloads intended for it. These payloads may contain sensitive information such as Wi-Fi or VPN configuration data, certificates, or other secrets delivered through MDM profiles.

This issue does not allow enrollment of new devices, administrative access to Fleet, or compromise of the Fleet control plane. Impact is limited to the targeted Windows device.

### Workarounds

If an immediate upgrade is not possible, affected Fleet users should temporarily disable Windows MDM.

### For more information

If you have any questions or comments about this advisory:

Email us at [security@fleetdm.com](mailto:security@fleetdm.com)
Join #fleet in [osquery Slack](https://join.slack.com/t/osquery/shared_invite/zt-h29zm0gk-s2DBtGUTW4CFel0f0IjTEw)

### Credits

We thank @secfox-ai for responsibly reporting this issue.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-2rc4-7jc6-qffh
- https://nvd.nist.gov/vuln/detail/CVE-2026-23998
- https://github.com/fleetdm/fleet/commit/3ff8119ab8f794806a4cc82e21f760c123d92966
- https://github.com/fleetdm/fleet
- https://github.com/fleetdm/fleet/releases/tag/fleet-v4.81.0
