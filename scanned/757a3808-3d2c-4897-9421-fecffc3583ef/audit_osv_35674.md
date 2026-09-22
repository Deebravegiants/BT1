# [H] Stack buffer overflow in Zephyr hl7800 modem driver parsing network-supplied +CGCONTRDP address fields

## Summary
Severity: High
Advisory: CVE-2026-12522
Aliases: GHSA-hchc-6489-w66v
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-12522
Type: osv

## Details
The HL7800 cellular modem driver's +CGCONTRDP: response handler on_cmd_atcmdinfo_ipaddr() in drivers/modem/vendor_standalone/hl7800.c parses the PDP-context dynamic parameters (local address, subnet mask, gateway, and DNS servers) that the cellular network assigns to the device. The response is linearized into a 256-byte stack buffer, after which each address field length is computed from comma/. delimiter positions in the network-supplied data and used directly as the length argument to strncpy() into the fixed 64-byte stack buffer temp_addr_str (and the 16-byte iface_ctx.dns_v4_string).

Because the field length is derived from attacker-controlled delimiter positions and was not bounded against the destination buffer, a single field can be far larger than 64 bytes. A malicious or impersonated cellular network (for example a rogue base station) can return a crafted +CGCONTRDP response with an overlong address field, causing strncpy() to write past temp_addr_str on the modem worker thread's stack, plus an out-of-bounds NUL write at temp_addr_str[addr_len].

No device-side privileges or user interaction are required: the device itself issues the AT+CGCONTRDP=1 query during normal network attach and parses whatever the network returns. The overflow corrupts adjacent stack memory in supervisor context, yielding at minimum a remotely triggerable crash and potentially control-flow hijacking on targets without stack protection.

The fix bounds every field length against its destination buffer (temp_addr_str and dns_v4_string) before each copy, rejecting overlong fields.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12522.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-hchc-6489-w66v
- https://nvd.nist.gov/vuln/detail/CVE-2026-12522
- https://github.com/zephyrproject-rtos/zephyr/commit/a1cbced64181bc0bdf95e1fd7118f2bb70cf679b
- https://github.com/zephyrproject-rtos/zephyr
