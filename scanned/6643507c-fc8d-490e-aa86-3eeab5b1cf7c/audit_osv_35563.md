# [H] Out-of-bounds access in Bluetooth ISO receive (`bt_iso_recv`) due to missing SDU-header length validation

## Summary
Severity: High
Advisory: CVE-2026-10658
Aliases: GHSA-26g8-rmpf-j6cw
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-10658
Type: osv

## Details
bt_iso_recv() in subsys/bluetooth/host/iso.c pulled the ISO SDU header (4 bytes) or, when the timestamp flag is set, the timestamped SDU header (8 bytes) from the inbound HCI ISO Data buffer via net_buf_pull_mem() without first checking buf->len. The upstream hci_iso() handler enforces buf->len == the controller-declared ISO Data_Load length, so a malicious or buggy controller / adjacent BLE peer on an established CIS/BIS can present a first-fragment (BT_ISO_START) or single (BT_ISO_SINGLE) PDU shorter than the SDU header. Because net_buf_simple_pull_mem only guards length with __ASSERT_NO_MSG (compiled out when CONFIG_ASSERT is disabled, the production default), the pull underflows buf->len (uint16_t, e.g. 0 - 8 = 0xFFF8) and advances buf->data past valid data: the subsequent reads of hdr->slen and hdr->sn are out-of-bounds reads of adjacent pool memory. For the multi-fragment (START) case the corrupted buffer is retained as iso->rx, and a following CONT/END fragment's net_buf_tailroom() guard underflows to a near-SIZE_MAX value, defeating the bounds check and causing net_buf_add_mem() to memcpy attacker-supplied fragment data far past the RX pool buffer (out-of-bounds write). The flaw affects ISO receive builds (CONFIG_BT_ISO_RX, selected by the default-off LE Audio options BT_ISO_PERIPHERAL/BT_ISO_CENTRAL/BT_ISO_SYNC_RECEIVER) and has existed since the ISO subsystem was introduced (v2.6.0) through v4.4.0. The fix adds explicit buf->len < sizeof(ts_hdr) and buf->len < sizeof(hdr) checks that drop the buffer before pulling.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10658.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-26g8-rmpf-j6cw
- https://nvd.nist.gov/vuln/detail/CVE-2026-10658
- https://github.com/zephyrproject-rtos/zephyr/commit/756b16b64317defefad36fc994316cf96e418708
- https://github.com/zephyrproject-rtos/zephyr
