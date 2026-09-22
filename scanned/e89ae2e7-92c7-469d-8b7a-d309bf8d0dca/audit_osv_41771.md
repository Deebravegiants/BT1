# [C] net: skmsg: preserve sg.copy across SG transforms

## Summary
Severity: Critical
Advisory: CVE-2026-63830
Ecosystem: Linux
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63830
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: skmsg: preserve sg.copy across SG transforms

The sk_msg sg.copy bitmap is part of the scatterlist entry ownership
state. A set bit tells sk_msg_compute_data_pointers() not to expose the
entry through writable BPF ctx->data. This protects entries backed by
pages that are not private to the sk_msg, such as splice-backed file
page-cache pages.

Several sk_msg transform paths move, copy, split, or compact
msg->sg.data[] entries without moving the matching sg.copy bit. This can
make an externally backed entry arrive at a new slot with a clear copy
bit. A later SK_MSG verdict can then expose sg_virt(sge) as writable
ctx->data and BPF stores can modify the original page cache.

Keep sg.copy synchronized with sg.data[] whenever entries are
transferred, shifted, split, or copied into a new sk_msg. Clear the bit
when an entry is replaced by a newly allocated private page or freed.
This covers the BPF pull/push/pop helpers, sk_msg_shift_left/right(),
sk_msg_xfer(), and tls_split_open_record(), including the partial tail
entry created during TLS open-record splitting.

## References
- https://git.kernel.org/stable/c/0eb4c16c4adb262763bda870a8ed38a1a9dec7ec
- https://git.kernel.org/stable/c/1acdd14c0990dd1cd4b6534f00366d2e6dfce05f
- https://git.kernel.org/stable/c/21ed9540a8e1906dfcbc1bb82ba9b4de4fa4bd6d
- https://git.kernel.org/stable/c/31a110642b5fb5e61940cbcfb503445ac4f28017
- https://git.kernel.org/stable/c/406e8a651a7b854c41fecd5117bb282b3a6c2c6b
- https://git.kernel.org/stable/c/9bb86d8184b37503816150c4a6ad3c17dfdbe827
- https://git.kernel.org/stable/c/d22cc92bc41290e5783a72375e0843d9435f6001
- https://git.kernel.org/stable/c/f126eed589eec6f201405abbc398844042ef6d57
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63830.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63830
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
