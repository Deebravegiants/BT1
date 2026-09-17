# [M] Out-of-bounds stack write in Zephyr virtio PCI driver from unvalidated device-supplied capability length

## Summary
Severity: Medium
Advisory: CVE-2026-13216
Aliases: GHSA-qrh3-4mvv-w667
CVSS: 6.1 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-13216
Type: osv

## Details
The virtio PCI driver (drivers/virtio/virtio_pci.c) parses a device's PCI capability list during driver initialization. In virtio_pci_read_cap() the device-supplied capability length byte cap_len (read from PCI config space via pcie_conf_read()) was only checked with assert(tmp.cap_len == cap_struct_size). That assert resolves to __ASSERT_NO_MSG(), gated by CONFIG_ASSERT, which defaults off in production builds, so the value reached the copy logic completely unvalidated.

The length then drives a loop that copies extra capability dwords into a fixed-size stack buffer supplied by the caller. A cap_len below the 24-byte base struct virtio_pci_cap underflows the unsigned extra_data_words count to a near-SIZE_MAX value, producing an effectively unbounded stack write; a cap_len above the caller's buffer (up to 255) writes up to roughly 228 bytes of device-controlled data past the buffer. Both are out-of-bounds writes of attacker-controlled content executed in kernel mode during boot-time device probe.

The input originates from the virtio device. In the common deployment where Zephyr runs as a guest under a hypervisor, the device backend is the host, which already fully outranks the guest, so the bug yields no privilege escalation. The exploitable case is a virtio device that is untrusted relative to the Zephyr kernel — an untrusted or physical/passthrough virtio PCIe device on a bare-metal system, or a confidential-computing posture where the guest must defend against the host — where a malicious device can corrupt the kernel stack and potentially achieve code execution or a crash.

The fix replaces the compiled-out assert with a runtime range check rejecting cap_len outside [sizeof(struct virtio_pci_cap), cap_struct_size] before any arithmetic or copy.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13216.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-qrh3-4mvv-w667
- https://nvd.nist.gov/vuln/detail/CVE-2026-13216
- https://github.com/zephyrproject-rtos/zephyr/commit/d98dacee24ad10c972d3b7281c9009d82ed351c9
- https://github.com/zephyrproject-rtos/zephyr
