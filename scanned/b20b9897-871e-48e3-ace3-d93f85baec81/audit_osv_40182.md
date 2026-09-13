# [H] bt: l2cap le coc: remote oob write via seg counter stored in net_buf user_data

## Summary
Severity: High
Advisory: CVE-2026-5068
Aliases: GHSA-qrcq-hxwj-mqxm
CVSS: 7.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-5068
Type: osv

## Details
A remote, unauthenticated BLE peer can trigger a 2-byte out-of-bounds write in the Bluetooth host during L2CAP LE CoC SDU reassembly. When the application enables segmentation (via chan_ops.alloc_buf) and the chosen RX pool has a user_data_size smaller than 2 bytes, the segmentation counter stored in the net_buf user_data area is written out of bounds in l2cap_chan_le_recv_seg (subsys/bluetooth/host/l2cap.c). The observed effects are an AddressSanitizer abort and, without ASan, heap corruption / fatal error.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5068.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-qrcq-hxwj-mqxm
- https://nvd.nist.gov/vuln/detail/CVE-2026-5068
- https://github.com/zephyrproject-rtos/zephyr
