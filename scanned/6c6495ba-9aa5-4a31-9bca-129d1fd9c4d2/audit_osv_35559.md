# [H] Bluetooth Classic SDP parser truncation bug in bt_sdp_parse_attribute() leads to reachable assertion and possible out-of-bounds read

## Summary
Severity: High
Advisory: CVE-2026-10651
Aliases: GHSA-p93g-3r68-cj53
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-10651
Type: osv

## Details
A malformed Bluetooth Classic SDP attribute can trigger a reachable assertion in Zephyr's SDP parser. In subsys/bluetooth/host/classic/sdp.c, bt_sdp_parse_attribute() accepts an input buffer once it contains the 1-byte attribute type and 2-byte attribute id, but then unconditionally pulls an additional byte for the value type without verifying that the byte is present. A truncated 3-byte attribute (for example 09 00 09) therefore reaches net_buf_simple_pull() with insufficient remaining length, triggering the __ASSERT_NO_MSG(buf->len >= len) check and a kernel panic in assert-enabled builds (denial of service). In builds where assertions are disabled, parsing may continue past the end of the available buffer, leading to an out-of-bounds read and undefined behavior.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10651.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-p93g-3r68-cj53
- https://nvd.nist.gov/vuln/detail/CVE-2026-10651
- https://github.com/zephyrproject-rtos/zephyr
