# [C] sctp: fix uninit-value in __sctp_rcv_asconf_lookup()

## Summary
Severity: Critical
Advisory: CVE-2026-53225
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53225
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: fix uninit-value in __sctp_rcv_asconf_lookup()

__sctp_rcv_asconf_lookup() in net/sctp/input.c only checks that the ASCONF
chunk can hold the ADDIP header and a parameter header, then calls
af->from_addr_param(), which reads the full address (16 bytes for IPv6)
trusting the parameter's declared length.

An unauthenticated peer can send a truncated trailing ASCONF chunk that
declares an IPv6 address parameter but stops after the 4-byte parameter
header; reached from the no-association lookup path, from_addr_param() then
reads uninitialized bytes past the parameter.

Impact: an unauthenticated SCTP peer makes the receive path read up to 16
bytes of uninitialized memory past a truncated ASCONF address parameter.

The sibling __sctp_rcv_init_lookup() bounds parameters with
sctp_walk_params(); this path open-codes the fetch and omits the bound.
Verify the whole address parameter lies within the chunk before
from_addr_param() reads it, the same class of fix as commit 51e5ad549c43
("net: sctp: fix KMSAN uninit-value in sctp_inq_pop").

## References
- https://git.kernel.org/stable/c/446e0ecd845abc394b24ae2030a883572bec9d16
- https://git.kernel.org/stable/c/8ce96f1182644079249a24ac7e2ffc32e0301a46
- https://git.kernel.org/stable/c/8e86817b8af4d552f3c6fe04ca52bb0c8c57411d
- https://git.kernel.org/stable/c/928dd94db23e8ba340f83d68f7f24d831b7a4426
- https://git.kernel.org/stable/c/d6bd0bb7697ea8c0387b0d9d973453f479017b23
- https://git.kernel.org/stable/c/d796cfd06074b579d265b28401306cadd30db945
- https://git.kernel.org/stable/c/f76a8b323e28e0951f979dbef20a7496383c47df
- https://git.kernel.org/stable/c/f8373d7090b745728de66308deeecc67e8d319ce
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53225.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53225
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
