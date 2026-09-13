# [H] net: nfc: nci: Add parameter validation for packet data

## Summary
Severity: High
Advisory: CVE-2025-40043
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40043
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.15.195, >=5.16.0 <6.1.156, >=6.2.0 <6.6.112, >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: nfc: nci: Add parameter validation for packet data

Syzbot reported an uninitialized value bug in nci_init_req, which was
introduced by commit 5aca7966d2a7 ("Merge tag
'perf-tools-fixes-for-v6.17-2025-09-16' of
git://git.kernel.org/pub/scm/linux/kernel/git/perf/perf-tools").

This bug arises due to very limited and poor input validation
that was done at nic_valid_size(). This validation only
validates the skb->len (directly reflects size provided at the
userspace interface) with the length provided in the buffer
itself (interpreted as NCI_HEADER). This leads to the processing
of memory content at the address assuming the correct layout
per what opcode requires there. This leads to the accesses to
buffer of `skb_buff->data` which is not assigned anything yet.

Following the same silent drop of packets of invalid sizes at
`nic_valid_size()`, add validation of the data in the respective
handlers and return error values in case of failure. Release
the skb if error values are returned from handlers in
`nci_nft_packet` and effectively do a silent drop

Possible TODO: because we silently drop the packets, the
call to `nci_request` will be waiting for completion of request
and will face timeouts. These timeouts can get excessively logged
in the dmesg. A proper handling of them may require to export
`nci_request_cancel` (or propagate error handling from the
nft packets handlers).

## References
- https://git.kernel.org/stable/c/0ba68bea1e356f466ad29449938bea12f5f3711f
- https://git.kernel.org/stable/c/74837bca0748763a77f77db47a0bdbe63b347628
- https://git.kernel.org/stable/c/8fcc7315a10a84264e55bb65ede10f0af20a983f
- https://git.kernel.org/stable/c/9c328f54741bd5465ca1dc717c84c04242fac2e1
- https://git.kernel.org/stable/c/bfdda0123dde406dbff62e7e9136037e97998a15
- https://git.kernel.org/stable/c/c395d1e548cc68e84584ffa2e3ca9796a78bf7b9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40043.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40043
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
