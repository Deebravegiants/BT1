# [H] net: pull headers in qdisc_pkt_len_segs_init()

## Summary
Severity: High
Advisory: CVE-2026-53091
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53091
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: pull headers in qdisc_pkt_len_segs_init()

Most ndo_start_xmit() methods expects headers of gso packets
to be already in skb->head.

net/core/tso.c users are particularly at risk, because tso_build_hdr()
does a memcpy(hdr, skb->data, hdr_len);

qdisc_pkt_len_segs_init() already does a dissection of gso packets.

Use pskb_may_pull() instead of skb_header_pointer() to make
sure drivers do not have to reimplement this.

Some malicious packets could be fed, detect them so that we can
drop them sooner with a new SKB_DROP_REASON_SKB_BAD_GSO drop_reason.

## References
- https://git.kernel.org/stable/c/7fb4c19670110f052c04e1ec1d2b953b9f4f57e4
- https://git.kernel.org/stable/c/9d4f5c68f5ad4ab425f3ce1500c97c9f9743999a
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53091.json
- https://access.redhat.com/errata/RHSA-2026:65334
- https://access.redhat.com/errata/RHSA-2026:66324
- https://access.redhat.com/errata/RHSA-2026:66325
- https://access.redhat.com/security/cve/CVE-2026-53091
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53091.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53091
- https://bugzilla.redhat.com/show_bug.cgi?id=2492270
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
