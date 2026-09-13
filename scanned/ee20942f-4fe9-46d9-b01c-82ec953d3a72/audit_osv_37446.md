# [H] NFC: digital: Bounds check NFC-A cascade depth in SDD response handler

## Summary
Severity: High
Advisory: CVE-2026-31622
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31622
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFC: digital: Bounds check NFC-A cascade depth in SDD response handler

The NFC-A anti-collision cascade in digital_in_recv_sdd_res() appends 3
or 4 bytes to target->nfcid1 on each round, but the number of cascade
rounds is controlled entirely by the peer device.  The peer sets the
cascade tag in the SDD_RES (deciding 3 vs 4 bytes) and the
cascade-incomplete bit in the SEL_RES (deciding whether another round
follows).

ISO 14443-3 limits NFC-A to three cascade levels and target->nfcid1 is
sized accordingly (NFC_NFCID1_MAXSIZE = 10), but nothing in the driver
actually enforces this.  This means a malicious peer can keep the
cascade running, writing past the heap-allocated nfc_target with each
round.

Fix this by rejecting the response when the accumulated UID would exceed
the buffer.

Commit e329e71013c9 ("NFC: nci: Bounds check struct nfc_target arrays")
fixed similar missing checks against the same field on the NCI path.

## References
- https://git.kernel.org/stable/c/1bec5698b55aa2be5c3b983dba657c01d0fd3dbc
- https://git.kernel.org/stable/c/20663102c14566e900e1d2f679e30b7f1694f387
- https://git.kernel.org/stable/c/2819f34e08bdffb6f06a51c67948ec5737fb166a
- https://git.kernel.org/stable/c/46ce8be2ced389bccd84bcc04a12cf2f4d0c22d1
- https://git.kernel.org/stable/c/5a59bf70c38ee1eb4be03bab830bbc3a6f0bd1f1
- https://git.kernel.org/stable/c/8d9d9bf3565271ca7ab9c716a94e87296177e7ba
- https://git.kernel.org/stable/c/9ba6bb09e00b922d902f684f575779e5433fe6e3
- https://git.kernel.org/stable/c/cc024a3de265ef6c58957f4990eccb9f806208cb
- https://git.kernel.org/stable/c/f83b399aa05a0712e3b1569a30d3d90b3533d2ef
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31622.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31622
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
