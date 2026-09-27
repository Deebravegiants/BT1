# [M] Out-of-bounds read via unvalidated stream_id in Intel ALH DAI get_properties

## Summary
Severity: Medium
Advisory: CVE-2026-12232
Aliases: GHSA-3557-j848-pv24
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-12232
Type: osv

## Details
The Intel ALH digital-audio-interface driver function dai_alh_get_properties() in drivers/dai/intel/alh/alh.c used a caller-supplied int stream_id with no range validation. The value indexes the fixed-size static const uint8_t alh_handshake_map[64] array and scales a FIFO register address, so an out-of-range stream_id produces an out-of-bounds read of one byte at an attacker-chosen signed offset from the array. That byte is written into prop->dma_hs_id and the resulting struct dai_properties is copied back to the caller, leaking it.

dai_get_properties_copy() is a Zephyr __syscall, and its verifier z_vrfy_dai_get_properties_copy() (drivers/dai/dai_handlers.c) validates only the device-object permission and the destination buffer, not stream_id. A user-mode thread that has been granted access to the ALH DAI device object can therefore call the syscall with an arbitrary stream_id, crossing the userspace/kernel sandbox boundary.

The impact is a one-byte-per-call arbitrary-offset kernel information disclosure (and leakage of a computed kernel address via fifo_address); a stream_id that resolves to an unmapped page faults in kernel context, giving a local denial of service. Exploitation requires CONFIG_USERSPACE and device access, making this a local, moderate-severity issue. The fix rejects negative and too-large stream_id values up front and returns NULL, which the copy wrapper maps to -ENOENT.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12232.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-3557-j848-pv24
- https://nvd.nist.gov/vuln/detail/CVE-2026-12232
- https://github.com/zephyrproject-rtos/zephyr/commit/b470bfce689809621cc5cd8c04a4eca93795827a
- https://github.com/zephyrproject-rtos/zephyr
