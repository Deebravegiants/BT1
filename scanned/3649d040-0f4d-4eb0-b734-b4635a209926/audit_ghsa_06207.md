# [H] Lima: An arbitrary user in a QEMU VM could gain the root privilege in the VM via the guest agent socket

## Summary
Severity: High
Advisory: GHSA-2j9v-p4xj-cjw2
CVE: CVE-2026-53657
CWE: CWE-276, CWE-668
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-14
Source: https://github.com/advisories/GHSA-2j9v-p4xj-cjw2
Type: github-advisory

## Affected
- Go: `github.com/lima-vm/lima/v2` — affected >=0 <2.1.3

## Details
### Impact
On an instance of Lima running with `qemu` driver, an arbitrary user in the VM could access `/run/lima-guestagent.sock` when the guest agent is enabled.

This could result in running an arbitrary command with the root privileges in the VM (**not on the host**), as `lima-guestagent.sock` provides the tunneling service for an arbitrary address, including a Unix socket address for privileged daemons like D-Bus.

This vulnerability is not exploitable on `vz` driver, as the guest agent uses vsocks instead of Unix sockets.

### Patches
Patched in Lima v2.1.3 (8a45892378d22f40505c31a38f786a07701b6d50)

> [!NOTE]
> The default user account in the VM can still run an arbitrary command as the root via the guest agent socket.
> This is not a vulnerability, as the user can already run an arbitrary command with `sudo` by design.

### Workarounds
- On macOS hosts, use `vz` driver instead of `qemu` (`limactl create --vm-type=vz`. Default since v1.0.)
- Or, disable the guest agent (`limactl create --plain`)

## References
- https://github.com/lima-vm/lima/security/advisories/GHSA-2j9v-p4xj-cjw2
- https://nvd.nist.gov/vuln/detail/CVE-2026-53657
- https://github.com/lima-vm/lima/commit/8a45892378d22f40505c31a38f786a07701b6d50
- https://github.com/lima-vm/lima/commit/b08cae8a670cf916d5da11c48a6de76dabd89678
- https://github.com/lima-vm/lima
- https://github.com/lima-vm/lima/releases/tag/v2.1.3
