# [H] Bluetooth: ISO: fix malformed ISO_END/CONT handling

## Summary
Severity: High
Advisory: CVE-2026-72334
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72334
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: ISO: fix malformed ISO_END/CONT handling

Core specification (Part C vol 4 sec 5.4.5) does not exclude empty
ISO_CONT, ISO_END packets.  We currently reject them if they are last.

If controller sends malformed sequence

    ISO_START -> rx_len = 4, ISO_CONT skb->len 4, ISO_START

that ends payload in ISO_CONT, we leak conn->rx_skb. If controller sends
too long ISO_END, we panic on skb_put. If controller sends too short
ISO_END we accept it.

Fix by marking unfinished ISO_START via conn->rx_skb != NULL.  Check
skb->len properly before skb_put.  Combine the ISO_CONT/END code paths
as they require the same initial checks. Reject too short ISO_END
packets.

## References
- https://git.kernel.org/stable/c/990e65eb9387c4ddfa7f68782b6644c2c35d489f
- https://git.kernel.org/stable/c/e054c1a6ae7310d2815778fddb87da616e11c255
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72334.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72334
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
