# [M] Infinite loop (DoS) in Bluetooth GATT client parsing of Read-By-Type responses with zero data length

## Summary
Severity: Medium
Advisory: CVE-2026-12236
Aliases: GHSA-483r-jq2x-5cp9
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-12236
Type: osv

## Details
The Bluetooth host GATT client function parse_read_std_char_desc() in subsys/bluetooth/host/gatt.c parses an ATT Read By Type Response received from a remote GATT server during BT_GATT_DISCOVER_STD_CHAR_DESC discovery. The per-entry stride rsp->len is taken directly from the peer's PDU, and the parse loop both tests its exit condition (length >= rsp->len) and advances (length -= rsp->len, pdu += rsp->len) using that value. The minimum value of rsp->len was never validated before the loop.

A malicious or malfunctioning peer can reply with rsp->len = 0. Because length is unsigned and never decreases, the loop condition stays true forever and the read pointer never advances; as long as the body is at least a few bytes with a non-zero handle and a matching descriptor UUID, the host repeatedly re-parses the same bytes and invokes the discovery callback, never terminating. This hangs the Bluetooth host processing thread (CWE-835, loop with unreachable exit condition).

The condition is reachable by any connected peer once the local device initiates standard-descriptor-value discovery; GATT discovery does not require bonding or encryption, so an unauthenticated adjacent attacker that the device connects to can trigger it. The impact is denial of service of the Bluetooth subsystem (and likely a watchdog reset on constrained targets); there is no memory disclosure or corruption.

The fix adds a rsp->len < sizeof(struct bt_att_data) check before the loop, rejecting under-length responses so the stride is always non-zero and the loop terminates. The sibling parsers parse_include() and parse_characteristic() already validated rsp->len and are unaffected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12236.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-483r-jq2x-5cp9
- https://nvd.nist.gov/vuln/detail/CVE-2026-12236
- https://github.com/zephyrproject-rtos/zephyr/commit/494283d469a95b294badaf45c639de433bf5e35a
- https://github.com/zephyrproject-rtos/zephyr
