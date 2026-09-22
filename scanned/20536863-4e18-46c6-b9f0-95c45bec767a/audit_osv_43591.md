# [H] rxrpc: rxrpc_verify_data ensure rx_dec_buffer alloc

## Summary
Severity: High
Advisory: CVE-2026-74435
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74435
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: rxrpc_verify_data ensure rx_dec_buffer alloc

rxrpc_recvmsg_data() calls rxrpc_verify_data() whenever the
rxrpc_call.rx_dec_buffer is unallocated and assumes that upon
successful return that rx_dec_buffer must be allocated.
However, rxrpc_verify_data() does not request an allocation if
the rxrpc_skb_priv.len is zero.

In addition, failure to allocate rx_dec_buffer will result in a
call to skb_copy_bits() with a NULL destination which can
trigger a NULL pointer dereference.

To prevent these issues rxrpc_verify_data() is modified to
always attempt to allocate the rxrpc_call.rx_dec_buffer if it
is NULL.

This issue was identified with assistance of a private
sashiko instance.

## References
- https://git.kernel.org/stable/c/16c8ae9735c5bd7e54dd7478d6348e0fc860842d
- https://git.kernel.org/stable/c/6563b4eb38c35d75892445bcf8aacdc29914821c
- https://git.kernel.org/stable/c/8bbede0afced346b24e4fbde0c68cf12980ba948
- https://git.kernel.org/stable/c/a962bc8508592c4d51092edac68579bd8b18fe44
- https://git.kernel.org/stable/c/d3b642cf95d48234590cc91450d8705a9bf6b540
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74435.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74435
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
