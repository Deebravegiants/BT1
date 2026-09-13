# [H] net: ena: Fix incorrect descriptor free behavior

## Summary
Severity: High
Advisory: CVE-2024-35958
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-35958
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.216, >=5.11.0 <5.15.156, >=5.16.0 <6.1.87, >=6.2.0 <6.6.28, >=6.7.0 <6.8.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ena: Fix incorrect descriptor free behavior

ENA has two types of TX queues:
- queues which only process TX packets arriving from the network stack
- queues which only process TX packets forwarded to it by XDP_REDIRECT
  or XDP_TX instructions

The ena_free_tx_bufs() cycles through all descriptors in a TX queue
and unmaps + frees every descriptor that hasn't been acknowledged yet
by the device (uncompleted TX transactions).
The function assumes that the processed TX queue is necessarily from
the first category listed above and ends up using napi_consume_skb()
for descriptors belonging to an XDP specific queue.

This patch solves a bug in which, in case of a VF reset, the
descriptors aren't freed correctly, leading to crashes.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/19ff8fed3338898b70b2aad831386c78564912e1
- https://git.kernel.org/stable/c/5c7f2240d9835a7823d87f7460d8eae9f4e504c7
- https://git.kernel.org/stable/c/b26aa765f7437e1bbe8db4c1641b12bd5dd378f0
- https://git.kernel.org/stable/c/bf02d9fe00632d22fa91d34749c7aacf397b6cde
- https://git.kernel.org/stable/c/c31baa07f01307b7ae05f3ce32b89d8e2ba0cc1d
- https://git.kernel.org/stable/c/fdfbf54d128ab6ab255db138488f9650485795a2
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35958.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35958
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
