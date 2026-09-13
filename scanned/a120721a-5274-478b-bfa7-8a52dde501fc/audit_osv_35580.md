# [H] Out-of-bounds access in Zephyr BR/EDR L2CAP configuration request handling via `uint16_t` length underflow

## Summary
Severity: High
Advisory: CVE-2026-10680
Aliases: GHSA-vrwx-p97q-8854
CVSS: 7.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-10680
Type: osv

## Details
The Classic (BR/EDR) L2CAP signaling handlers l2cap_br_conf_req() and l2cap_br_conf_rsp() in subsys/bluetooth/host/classic/l2cap_br.c validated the minimum command size against buf->len (the bytes remaining in the whole received PDU) instead of len (the per-command data length from the L2CAP signaling header). Because multiple signaling commands can be packed into one PDU, buf->len may exceed a command's len. An attacker can send a CONF_REQ command with a header length smaller than the configuration-request structure (e.g. 0), followed by another command so that buf->len still satisfies the check. The check then passes incorrectly and opt_len = len - sizeof(*req) underflows the uint16_t to a near-0xFFFF value. The configuration-option loop, which lacks an opt_len-versus-buf->len guard, then walks far past the end of the pooled ACL receive buffer using net_buf pull primitives that perform no runtime bounds check, producing an out-of-bounds read of host memory and, when the out-of-bounds option bytes encode an MTU or flush-timeout option, an out-of-bounds write. The BR/EDR signaling channel is processed before pairing/encryption and an L2CAP channel to an L0 service such as SDP can be opened without pairing, so an unauthenticated peer within radio range that can establish an ACL connection can trigger the flaw, leading to memory corruption and denial of service (host/device crash). The defect is present in released versions including v4.4.0. The fix validates against len instead of buf->len in both handlers.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10680.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-vrwx-p97q-8854
- https://nvd.nist.gov/vuln/detail/CVE-2026-10680
- https://github.com/zephyrproject-rtos/zephyr/commit/1d451683377f4c8e56d7718565bea7b5c1155159
- https://github.com/zephyrproject-rtos/zephyr
