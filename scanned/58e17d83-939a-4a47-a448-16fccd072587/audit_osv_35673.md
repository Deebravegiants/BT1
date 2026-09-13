# [M] Stack buffer overflow and off-by-one writes in Zephyr HL7800 modem AT response handlers

## Summary
Severity: Medium
Advisory: CVE-2026-12520
Aliases: GHSA-9xc4-j5x8-v6jx
CVSS: 6.4 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-12520
Type: osv

## Details
The Sierra Wireless HL7800 cellular modem driver (drivers/modem/vendor_standalone/hl7800.c, located at drivers/modem/hl7800.c in v4.4.0 and earlier) parses AT responses with roughly twenty handlers that call net_buf_linearize(value, sizeof(value), *buf, 0, len) into a 128-byte stack buffer and then write value[out_len] = 0. Because net_buf_linearize() (lib/net_buf/buf.c) can return a count equal to its destination-length argument, a field that exactly fills the buffer makes the terminating NUL land one byte past the end, a single-byte out-of-bounds write into adjacent stack memory.

The +KCELLMEAS cell-measurement handler on_cmd_atcmdinfo_rssi() is worse: it passed the wire length len as the destination size (net_buf_linearize(value, len, *buf, 0, len)), so a response line longer than 128 bytes overflows the value stack buffer with attacker-influenceable content. The line length comes from net_buf_findcrlf(), which accumulates bytes across the whole net_buf fragment chain and is not bounded to 128, so an over-long line reaches the defect.

The data originates from the cellular modem over UART, driven by the network: operator-scan results, +CGCONTRDP IP/DNS info, socket indications, and +KCELLMEAS neighbour-cell reports. An attacker able to shape what the modem emits — a rogue base station, a compromised modem baseband, or a remote peer feeding oversized response framing — can drive a line past 128 bytes. The handlers run in the driver's RX thread in kernel context, so the corruption is kernel-side.

The +KCELLMEAS path is a full stack buffer overflow whose worst case is code execution in kernel context and whose floor is a reliable crash; the remaining sites are single-byte NUL out-of-bounds writes. Exploitation requires the modem to emit an over-long AT response line, giving high attack complexity over an adjacent (cellular radio) vector. The fix passes sizeof(dst) - 1 (and correct explicit bounds for the IMSI and +KCELLMEAS sites) so the terminator always stays in bounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12520.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-9xc4-j5x8-v6jx
- https://nvd.nist.gov/vuln/detail/CVE-2026-12520
- https://github.com/zephyrproject-rtos/zephyr/commit/ea91f9375677aa4268e4044e096902dbe789f101
- https://github.com/zephyrproject-rtos/zephyr
