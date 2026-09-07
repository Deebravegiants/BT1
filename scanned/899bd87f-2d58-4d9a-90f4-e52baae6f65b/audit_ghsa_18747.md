# [H] NeuVector telemetry sender is vulnerable to MITM and DoS

## Summary
Severity: High
Advisory: GHSA-qqj3-g7mx-5p4w
CVE: CVE-2025-54470
CWE: CWE-295, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2025-10-21
Source: https://github.com/advisories/GHSA-qqj3-g7mx-5p4w
Type: github-advisory

## Affected
- Go: `github.com/neuvector/neuvector` — affected >=0.0.0-20230727023453-1c4957d53911 <0.0.0-20251020133207-084a437033b4

## Details
### Impact
This vulnerability affects NeuVector deployments only when the `Report anonymous cluster data option` is enabled. When this option is enabled, NeuVector sends anonymous telemetry data to the telemetry server at `https://upgrades.neuvector-upgrade-responder.livestock.rancher.io`.

In affected versions, NeuVector does not enforce TLS certificate verification when transmitting anonymous cluster data to the telemetry server. As a result, the communication channel is susceptible to man-in-the-middle (MITM) attacks, where an attacker could intercept or modify the transmitted data. Additionally, NeuVector loads the response of the telemetry server is loaded into memory without size limitation, which makes  it vulnerable to a Denial of Service(DoS) attack. 

The patched version includes the following security improvements:
- NeuVector now verifies the telemetry server’s `TLS certificate chain` and `hostname` during the handshake process. This ensures that all telemetry communications occur over a trusted and verified channel.
- NeuVector limits the telemetry server’s response to `256 bytes`, mitigating the risk of memory exhaustion and DoS attacks.

These security enhancements are enabled by default and require no user action.


### Patches
Patched versions include release **v5.4.7** and above.

### Workarounds
If you cannot update to a patched version, you can temporarily disable the Report anonymous cluster data, which is enabled by default in NeuVector.
To change this setting, go to **Settings** → **Configuration** → **Report anonymous cluster data** in the NeuVector UI.

Disabling this option prevents NeuVector from sending telemetry data to the telemetry server, which helps mitigate this vulnerability.


### References
If you have any questions or comments about this advisory:
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [NeuVector](https://github.com/neuvector/neuvector/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-neuvector/support-matrix/all-supported-versions/neuvector-v-all-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/#suse-security).

## References
- https://github.com/neuvector/neuvector/security/advisories/GHSA-qqj3-g7mx-5p4w
- https://nvd.nist.gov/vuln/detail/CVE-2025-54470
- https://github.com/neuvector/neuvector/commit/06424701e69bf1eb76ff90180d78853fded93021
- https://github.com/neuvector/neuvector/commit/415737cbec581a5dc5f204fac1c78b7f29ad7dc2
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2025-54470
- https://github.com/neuvector/neuvector
