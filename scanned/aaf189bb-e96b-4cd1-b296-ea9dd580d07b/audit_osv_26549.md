# [H] netfilter: conntrack: dccp: copy entire header to stack buffer, not just basic one

## Summary
Severity: High
Advisory: CVE-2023-53333
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53333
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.26 <5.4.251, >=5.5.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: conntrack: dccp: copy entire header to stack buffer, not just basic one

Eric Dumazet says:
  nf_conntrack_dccp_packet() has an unique:

  dh = skb_header_pointer(skb, dataoff, sizeof(_dh), &_dh);

  And nothing more is 'pulled' from the packet, depending on the content.
  dh->dccph_doff, and/or dh->dccph_x ...)
  So dccp_ack_seq() is happily reading stuff past the _dh buffer.

BUG: KASAN: stack-out-of-bounds in nf_conntrack_dccp_packet+0x1134/0x11c0
Read of size 4 at addr ffff000128f66e0c by task syz-executor.2/29371
[..]

Fix this by increasing the stack buffer to also include room for
the extra sequence numbers and all the known dccp packet type headers,
then pull again after the initial validation of the basic header.

While at it, mark packets invalid that lack 48bit sequence bit but
where RFC says the type MUST use them.

Compile tested only.

v2: first skb_header_pointer() now needs to adjust the size to
    only pull the generic header. (Eric)

Heads-up: I intend to remove dccp conntrack support later this year.

## References
- https://git.kernel.org/stable/c/26bd1f210d3783a691052c51d76bb8a8bbd24c67
- https://git.kernel.org/stable/c/337fdce450637ea663bc816edc2ba81e5cdad02e
- https://git.kernel.org/stable/c/5c618daa5038712c4a4ef8923905a2ea1b8836a1
- https://git.kernel.org/stable/c/8c0980493beed3a80d6329c44ab293dc8c032927
- https://git.kernel.org/stable/c/9bdcda7abaf22f6453e5b5efb7eb4e524095d5d8
- https://git.kernel.org/stable/c/c052797ac36813419ad3bfa54cb8615db4b41f15
- https://git.kernel.org/stable/c/ff0a3a7d52ff7282dbd183e7fc29a1fe386b0c30
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53333.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53333
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
