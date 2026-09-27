# [H] net: gtp: Fix Use-After-Free in gtp_dellink

## Summary
Severity: High
Advisory: CVE-2024-27396
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2024-27396
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.313, >=4.20.0 <5.4.275, >=5.5.0 <5.15.158, >=5.11.0 <6.1.90, >=5.16.0 <6.6.30, >=6.2.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: gtp: Fix Use-After-Free in gtp_dellink

Since call_rcu, which is called in the hlist_for_each_entry_rcu traversal
of gtp_dellink, is not part of the RCU read critical section, it
is possible that the RCU grace period will pass during the traversal and
the key will be free.

To prevent this, it should be changed to hlist_for_each_entry_safe.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/07b20d0a3dc13fb1adff10b60021a4924498da58
- https://git.kernel.org/stable/c/0caff3e6390f840666b8dc1ecebf985c2ef3f1dd
- https://git.kernel.org/stable/c/25a1c2d4b1fcf938356a9688a96a6456abd44b29
- https://git.kernel.org/stable/c/2aacd4de45477582993f8a8abb9505a06426bfb6
- https://git.kernel.org/stable/c/2e74b3fd6bf542349758f283676dff3660327c07
- https://git.kernel.org/stable/c/718df1bc226c383dd803397d7f5d95557eb81ac7
- https://git.kernel.org/stable/c/cd957d1716ec979d8f5bf38fc659aeb9fdaa2474
- https://git.kernel.org/stable/c/f2a904107ee2b647bb7794a1a82b67740d7c8a64
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27396.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27396
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
