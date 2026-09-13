# [H] Flannel has cross-node remote code execution via extension backend BackendData injection

## Summary
Severity: High
Advisory: GHSA-vchx-5pr6-ffx2
CVE: CVE-2026-32241
CWE: CWE-77, CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-vchx-5pr6-ffx2
Type: github-advisory

## Affected
- Go: `github.com/flannel-io/flannel` — affected >=0 <0.28.2

## Details
### Background
The Flannel project includes an experimental Extension backend that allows users to easily prototype new backend types. This backend uses shell commands stored in Kubernetes annotations to configure network connectivity on the node.

Note: consumers are only affected by this vulnerability if they use the experimental Extension backend. Other backends such as vxlan and wireguard are unaffected.

### Vulnerability
This Extension backend is vulnerable to a command injection that allows an attacker who can set Kubernetes Node annotations to achieve root-level arbitrary command execution on every flannel node in the cluster.

The Extension backend's SubnetAddCommand and SubnetRemoveCommand receive attacker-controlled data via stdin (from the `flannel.alpha.coreos.com/backend-data` Node annotation). The content of this annotation is unmarshalled and piped directly to a shell command without checks.

### Impact
Kubernetes clusters using Flannel with the Extension backend are affected by this vulnerability. Other backends such as vxlan and wireguard are unaffected.

### Patches
This is fixed in version v0.28.2.

### Workaround 
If consumers cannot update to a patched version, then use Flannel with another backend such as vxlan or wireguard.

### Credits
Flannel would like to thank  Shachar Tal from Palo Alto Networks for reporting this vulnerability.

## References
- https://github.com/flannel-io/flannel/security/advisories/GHSA-vchx-5pr6-ffx2
- https://nvd.nist.gov/vuln/detail/CVE-2026-32241
- https://github.com/flannel-io/flannel/commit/08bc9a4c990ae785d2fcb448f4991b58485cd26a
- https://github.com/flannel-io/flannel
- https://github.com/flannel-io/flannel/releases/tag/v0.28.2
