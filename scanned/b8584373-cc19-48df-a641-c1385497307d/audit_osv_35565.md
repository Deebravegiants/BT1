# [M] Shared reassembly buffer in Bluetooth BAP Broadcast Assistant enables cross-connection memory corruption

## Summary
Severity: Medium
Advisory: CVE-2026-10660
Aliases: GHSA-73c7-3rh7-v5p9
CVSS: 6.4 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-07-11
Source: https://osv.dev/vulnerability/CVE-2026-10660
Type: osv

## Details
The Bluetooth BAP Broadcast Assistant GATT client in subsys/bluetooth/audio/bap_broadcast_assistant.c reassembled remote Broadcast Receive State data into a single file-static net_buf_simple (att_buf, BT_ATT_MAX_ATTRIBUTE_LEN = 512 bytes) shared by all connection instances, while the BUSY flag, long-read handle, and reset/offset state were per-connection.

When the device acts as a Broadcast Assistant connected to multiple Scan Delegator peripherals, notification and long-read callbacks from different connections interleave on the shared buffer: the append in notify_handler (net_buf_simple_add_mem at the not-busy branch) performs no tailroom check, so receive-state notifications from two or more delegators accumulate on the same 512-byte buffer and, with a sufficiently large configured ATT MTU (BT_L2CAP_TX_MTU up to 2000) and two-to-three concurrent connections, write past the buffer into adjacent .bss (net_buf_simple_add only asserts in debug builds).

Even below the overflow threshold, one connection's net_buf_simple_reset zeroes the shared length while another connection's reassembly and GATT read offset are in flight, mixing one peer's data into another's parse. A malicious or compromised Scan Delegator (or two colluding peers) over BLE can trigger this, causing out-of-bounds writes (memory corruption / denial of service) and cross-connection data corruption.

The fix moves the buffer into the per-connection instance struct so each connection reassembles into its own buffer. Affects Zephyr releases shipping the Broadcast Assistant with the shared buffer, including v4.4.0 and earlier.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10660.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-73c7-3rh7-v5p9
- https://nvd.nist.gov/vuln/detail/CVE-2026-10660
- https://github.com/zephyrproject-rtos/zephyr/commit/0cd61589ff820b6a585c73cb36f1e14b043a2795
- https://github.com/zephyrproject-rtos/zephyr
