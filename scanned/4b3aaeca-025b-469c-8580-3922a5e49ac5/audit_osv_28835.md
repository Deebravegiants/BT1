# [H] net: core: reject skb_copy(_expand) for fraglist GSO skbs

## Summary
Severity: High
Advisory: CVE-2024-36929
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36929
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.217, >=5.11.0 <5.15.159, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: core: reject skb_copy(_expand) for fraglist GSO skbs

SKB_GSO_FRAGLIST skbs must not be linearized, otherwise they become
invalid. Return NULL if such an skb is passed to skb_copy or
skb_copy_expand, in order to prevent a crash on a potential later
call to skb_gso_segment.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/989bf6fd1e1d058e73a364dce1a0c53d33373f62
- https://git.kernel.org/stable/c/aea5e2669c2863fdd8679c40ee310b3bcaa85aec
- https://git.kernel.org/stable/c/c7af99cc21923a9650533c9d77265c8dd683a533
- https://git.kernel.org/stable/c/cfe34d86ef9765c388f145039006bb79b6c81ac6
- https://git.kernel.org/stable/c/d091e579b864fa790dd6a0cd537a22c383126681
- https://git.kernel.org/stable/c/faa83a7797f06cefed86731ba4baa3b4dfdc06c1
- https://lists.debian.org/debian-lts-announce/2024/06/msg00019.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36929.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36929
- https://security.netapp.com/advisory/ntap-20240905-0010/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
