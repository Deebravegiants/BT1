# [M] usb: gadget: f_ncm: validate minimum block_len in ncm_unwrap_ntb()

## Summary
Severity: Medium
Advisory: CVE-2026-31617
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31617
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: gadget: f_ncm: validate minimum block_len in ncm_unwrap_ntb()

The block_len read from the host-supplied NTB header is checked against
ntb_max but has no lower bound. When block_len is smaller than
opts->ndp_size, the bounds check of:
	ndp_index > (block_len - opts->ndp_size)
will underflow producing a huge unsigned value that ndp_index can never
exceed, defeating the check entirely.

The same underflow occurs in the datagram index checks against block_len
- opts->dpe_size.  With those checks neutered, a malicious USB host can
choose ndp_index and datagram offsets that point past the actual
transfer, and the skb_put_data() copies adjacent kernel memory into the
network skb.

Fix this by rejecting block lengths that cannot hold at least the NTB
header plus one NDP.  This will make block_len - opts->ndp_size and
block_len - opts->dpe_size both well-defined.

Commit 8d2b1a1ec9f5 ("CDC-NCM: avoid overflow in sanity checking") fixed
a related class of issues on the host side of NCM.

## References
- https://git.kernel.org/stable/c/068a7f2749fff6462a0a908ec415b885fe430f50
- https://git.kernel.org/stable/c/0f156bb5334e588034ca68ac2ee92b23f66e56e7
- https://git.kernel.org/stable/c/1425655c2870054c3ab4712e2b6dbdd331597ada
- https://git.kernel.org/stable/c/6762f8a95772265dd0c2ffe7f400493f3115b135
- https://git.kernel.org/stable/c/74908b0318d1df1188457040b8714ff4d4b68126
- https://git.kernel.org/stable/c/8757a2593631443648218244b9788e193ae0fdc1
- https://git.kernel.org/stable/c/8b3b7bd3c02f98634baaf36c7fc7ac915f6517ca
- https://git.kernel.org/stable/c/8f993d30b95dc9557a8a96ceca11abed674c8acb
- https://git.kernel.org/stable/c/d58ba8f6546232f8414f396c189297dbee03f1a7
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-31617.json
- https://access.redhat.com/security/cve/CVE-2026-31617
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31617.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31617
- https://bugzilla.redhat.com/show_bug.cgi?id=2461448
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
