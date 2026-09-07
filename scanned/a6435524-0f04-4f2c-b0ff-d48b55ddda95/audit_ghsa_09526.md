# [H] Harvester's SUSE Virtualization Registration Client Vulnerable to MITM and DOS

## Summary
Severity: High
Advisory: GHSA-pgh9-mpwc-8jjf
CVE: CVE-2025-71261
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-pgh9-mpwc-8jjf
Type: github-advisory

## Affected
- Go: `github.com/harvester/harvester` — affected >=0 <1.8.0

## Details
### Impact

A vulnerability has been identified in the [SUSE Virtualization (Harvester) Rancher integration mechanism](https://docs.harvesterhci.io/v1.7/rancher/rancher-integration) where by default the registration client uses an insecure TLS option that fails to verify  the remote server’s certificate. This security gap could allow the execution of a man-in-the-middle (MitM) attack against SUSE Virtualization.

An attacker with network-level access between the SUSE Virtualization and Rancher Manager could interfere with the TLS handshake and abuse it to bypass TLS as a security control. The registration client could be misled to send cluster registration requests to an impersonated remote service. Additionally, because the system processes response payloads without performing size validation, an attacker could induce a memory buffer overflow, leading to a potential crash of the SUSE Virtualization registration controller.

Note that this vulnerability only affects the cluster registration configuration (the `cluster-registration-url` setting) which is distinct from the secured configuration used to maintain operational connectivity between SUSE Virtualization and Rancher Manager, as well as between the manager and hosted downstream clusters.

Please consult the associated[ MITRE ATT&CK - Technique - Adversary-in-the-Middle](https://attack.mitre.org/techniques/T1557/) and [MITRE ATT&CK - Technique - Endpoint Denial of Service: Application or System Exploitation](https://attack.mitre.org/techniques/T1499/004/) for further information about this category of attack.

### Patches

This vulnerability is addressed by updating the registration client’s default behaviour to validate the certificate presented by the remote server against the list of trusted system root certificate authority (CA) and those defined by the `additional-ca` setting.

Patched versions of SUSE Virtualization include releases v1.8.0 or newer.

### Workarounds

If developers can't upgrade to a fixed version, ensure that only authorized cluster administrators can access and modify the `cluster-registration-url` setting.

### Resources

If there are any questions or comments about this advisory:
* Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
* Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
* Verify with SUSE [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/harvester/harvester/security/advisories/GHSA-pgh9-mpwc-8jjf
- https://nvd.nist.gov/vuln/detail/CVE-2025-71261
- https://github.com/harvester/harvester
