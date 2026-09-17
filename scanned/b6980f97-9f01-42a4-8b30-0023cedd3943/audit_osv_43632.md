# [H] Bluetooth: HIDP: validate numbered report payloads

## Summary
Severity: High
Advisory: CVE-2026-74507
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74507
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: HIDP: validate numbered report payloads

When hidp_get_raw_report() waits for a numbered report,
hidp_process_data() compares the expected report number with skb->data[0].
A connected HIDP peer can reply with only a DATA transaction header,
leaving the skb empty after the header is removed.

KMSAN reports an uninitialized-value use in hidp_session_run(), with the
value originating in __alloc_skb() through vhci_write(). The transaction
header checks remove the empty-frame reports, but this report remains until
the payload check is added.

The comparison can also consume a peer-controlled byte beyond the declared
L2CAP PDU. A DATA | FEATURE response followed by an extra 0x01 byte made
the current code accept that byte as report ID 1 and complete
HIDIOCGFEATURE with a zero-byte result. With this change the malformed
response is rejected with -EIO, while a subsequent valid response still
succeeds.

Require a payload byte before comparing a numbered report ID. Unnumbered
reports continue to accept an empty payload.

## References
- https://git.kernel.org/stable/c/011bf4350d941f1995b2bd4b815ee206cacf2b8e
- https://git.kernel.org/stable/c/27cc0e603355c585f1e5da8398faa4d36d498188
- https://git.kernel.org/stable/c/34f53d27b81a16a02828c8fdfa4e02badc326f17
- https://git.kernel.org/stable/c/689d8bb7fee96b7196b572b015b6055c6616ce0c
- https://git.kernel.org/stable/c/7e7162427659b70ea17cd41b1f79e2e64c246690
- https://git.kernel.org/stable/c/9c841f59e10b5d75c398a3fc6b2da448d2a2276b
- https://git.kernel.org/stable/c/b7ad105d46acd828e424454815e4cd31069e047a
- https://git.kernel.org/stable/c/c73beb320f5705e508bf7d385b8cc5ef8d9c8b69
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74507.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74507
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
