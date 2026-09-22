# [H] netfilter: complete validation of user input

## Summary
Severity: High
Advisory: CVE-2024-35962
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-35962
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.215 <5.10.216, >=5.15.154 <5.15.156, >=6.1.85 <6.1.87, >=6.6.26 <6.6.28, >=6.8.5 <6.8.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: complete validation of user input

In my recent commit, I missed that do_replace() handlers
use copy_from_sockptr() (which I fixed), followed
by unsafe copy_from_sockptr_offset() calls.

In all functions, we can perform the @optlen validation
before even calling xt_alloc_table_info() with the following
check:

if ((u64)optlen < (u64)tmp.size + sizeof(tmp))
        return -EINVAL;

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/562b7245131f6e9f1d280c8b5a8750f03edfc05c
- https://git.kernel.org/stable/c/65acf6e0501ac8880a4f73980d01b5d27648b956
- https://git.kernel.org/stable/c/89242d9584c342cb83311b598d9e6b82572eadf8
- https://git.kernel.org/stable/c/97dab36e57c64106e1c8ebd66cbf0d2d1e52d6b7
- https://git.kernel.org/stable/c/c760089aa98289b4b88a7ff5a62dd92845adf223
- https://git.kernel.org/stable/c/cf4bc359b76144a3dd55d7c09464ef4c5f2b2b05
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35962.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35962
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
