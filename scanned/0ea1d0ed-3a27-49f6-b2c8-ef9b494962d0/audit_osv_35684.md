# [M] Out-of-bounds read in Zephyr PTP message parsing from unvalidated message type

## Summary
Severity: Medium
Advisory: CVE-2026-12632
Aliases: GHSA-frjr-h396-7wh4
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-12632
Type: osv

## Details
Zephyr's Precision Time Protocol receive handler ptp_msg_post_recv() in subsys/net/lib/ptp/msg.c takes the 4-bit message type straight off the wire via ptp_msg_type() (msg->header.type_major_sdo_id & 0xF, range 0-15) and uses it to index the msg_size[] table. That table only defines entries up to PTP_MSG_MANAGEMENT (0xD), giving it ARRAY_SIZE == 14. Before the fix there was no upper-bound check, so the undefined types 0xE and 0xF indexed one or two int slots past the end of the array — an out-of-bounds read of adjacent read-only data.

The out-of-bounds value is then reused as a length: it gates msg_size[type] > cnt, and when it is small or negative it makes cnt - msg_size[type] a large positive budget passed to msg_tlv_post_recv(), whose TLV loop then walks the message suffix past the received bytes, performing further out-of-bounds reads and in-place byte-swap writes on memory beyond the message slab.

The defect is reached directly from the network: ptp_port_event_gen() in subsys/net/lib/ptp/port.c reads a PTP frame with ptp_transport_recv() and calls ptp_msg_post_recv() with the attacker-chosen type. PTP uses UDP multicast or raw Ethernet (0x88F7) and is unauthenticated, so any host on the same link can trigger the indexing on a CONFIG_PTP-enabled node with no preconditions.

The reliably reproducible impact is a denial of service (fault/crash); a limited memory-corruption path exists but depends on the build-specific value adjacent to msg_size[], which the attacker cannot tune. The fix rejects type >= ARRAY_SIZE(msg_size) with -EBADMSG before any indexing.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12632.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-frjr-h396-7wh4
- https://nvd.nist.gov/vuln/detail/CVE-2026-12632
- https://github.com/zephyrproject-rtos/zephyr/commit/30dabd4c2f2e3641732c00111cd80b5c524c0136
- https://github.com/zephyrproject-rtos/zephyr
