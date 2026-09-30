# [M] Out-of-bounds write caused by an integer underflow in the Bluetooth Mesh subsystem.

## Summary
Severity: Medium
Advisory: CVE-2026-5589
Aliases: GHSA-4pm9-4v7f-x6gr
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-06-04
Source: https://osv.dev/vulnerability/CVE-2026-5589
Type: osv

## Details
An integer underflow in bt_mesh_sol_recv() in the Bluetooth Mesh solicitation handling (subsys/bluetooth/mesh/solicitation.c) leads to an out-of-bounds write. When CONFIG_BT_MESH_OD_PRIV_PROXY_SRV is enabled, the function parses solicitation PDUs from raw BLE advertising payloads. The AD parsing loop reads an attacker-controlled length byte (reported_len) and computes reported_len - 3 without checking that reported_len >= 3. When reported_len is less than 3, the subtraction is performed in signed int arithmetic and yields a negative value that bypasses the length guard and is then implicitly converted to a very large size_t when passed to net_buf_simple_pull_mem(). In builds without assertions, this wraps the buffer length and advances the data pointer far out of bounds, so subsequent reads dereference invalid memory. A nearby BLE device can trigger this with a non-connectable advertisement carrying a UUID16 AD structure and a crafted length byte, with no pairing or prior association required, potentially leading to denial of service or arbitrary code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5589.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-4pm9-4v7f-x6gr
- https://nvd.nist.gov/vuln/detail/CVE-2026-5589
- https://github.com/zephyrproject-rtos/zephyr
