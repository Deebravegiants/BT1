# [H] sctp: avoid NULL dereference when chunk data buffer is missing

## Summary
Severity: High
Advisory: CVE-2025-40240
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-40240
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.196, >=5.16.0 <6.1.158, >=6.2.0 <6.6.115, >=6.7.0 <6.12.56, >=6.13.0 <6.17.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: avoid NULL dereference when chunk data buffer is missing

chunk->skb pointer is dereferenced in the if-block where it's supposed
to be NULL only.

chunk->skb can only be NULL if chunk->head_skb is not. Check for frag_list
instead and do it just before replacing chunk->skb. We're sure that
otherwise chunk->skb is non-NULL because of outer if() condition.

## References
- https://git.kernel.org/stable/c/03e80a4b04ef1fb2c61dd63216ab8d3a5dcb196f
- https://git.kernel.org/stable/c/08165c296597075763130919f2aae59b5822f016
- https://git.kernel.org/stable/c/441f0647f7673e0e64d4910ef61a5fb8f16bfb82
- https://git.kernel.org/stable/c/4f6da435fb5d8a21cbf8cae5ca5a2ba0e1012b71
- https://git.kernel.org/stable/c/61cda2777b07d27459f5cac5a047c3edf9c8a1a9
- https://git.kernel.org/stable/c/7a832b0f99be19df608cb75c023f8027b1789bd1
- https://git.kernel.org/stable/c/89b465b54227c245ddc7cc9ed822231af21123ef
- https://git.kernel.org/stable/c/cb9055ba30306ede4ad920002233d0659982f1cb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40240.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40240
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
