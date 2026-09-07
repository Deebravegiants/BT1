# [H] Steve doesn’t verify a server’s certificate and is susceptible to man-in-the-middle (MitM) attacks

## Summary
Severity: High
Advisory: GHSA-95fc-g4gj-mqmx
CVE: CVE-2023-32198
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-25
Source: https://github.com/advisories/GHSA-95fc-g4gj-mqmx
Type: github-advisory

## Affected
- Go: `github.com/rancher/steve` — affected >=0.2.0 <0.2.1
- Go: `github.com/rancher/steve` — affected >=0.3.0 <0.3.3
- Go: `github.com/rancher/steve` — affected >=0.4.0 <0.4.4
- Go: `github.com/rancher/steve` — affected >=0.5.0 <0.5.13

## Details
### Impact
A vulnerability has been identified in Steve where by default it was using an insecure option that did not validate the certificate presented by the remote server while performing a TLS connection. This could allow the execution of a man-in-the-middle (MitM) attack against services using Steve.

For example, Rancher relies on Steve as a dependency for its user interface (UI) to proxy requests to Kubernetes clusters. Users who have the permission to create a service in Rancher’s local cluster can take over Rancher’s UI and display their own UI to gather sensitive information. This is only possible when the setting `ui-offline-preferred` is manually set to `remote` (by default Rancher sets it to `dynamic`). This enables further attacks such as cross-site scripting (XSS), or tampering the UI to collect passwords from other users etc.

Please consult the associated  [MITRE ATT&CK - Technique - Adversary-in-the-Middle](https://attack.mitre.org/techniques/T1557/) for further information about this category of attack.

### Patches
Patched versions of Steve include releases `v0.2.1`, `v0.3.3`, `v0.4.4` and `v0.5.13`.

This vulnerability is addressed by changing Steve to always verify a server’s certificate based on Go’s TLS settings.

### Workarounds
If you can't upgrade to a fixed version, please make sure that you are only using Steve to connect to trusted servers.

### References
If you have any questions or comments about this advisory:
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/steve/security/advisories/GHSA-95fc-g4gj-mqmx
- https://github.com/rancher/steve
- https://pkg.go.dev/vuln/GO-2025-3648
