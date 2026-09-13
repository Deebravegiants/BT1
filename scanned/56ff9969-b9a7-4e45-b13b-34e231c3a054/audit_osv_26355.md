# [H] netfilter: allow exp not to be removed in nf_ct_find_expectation

## Summary
Severity: High
Advisory: CVE-2023-52927
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-14
Source: https://osv.dev/vulnerability/CVE-2023-52927
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.130

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: allow exp not to be removed in nf_ct_find_expectation

Currently nf_conntrack_in() calling nf_ct_find_expectation() will
remove the exp from the hash table. However, in some scenario, we
expect the exp not to be removed when the created ct will not be
confirmed, like in OVS and TC conntrack in the following patches.

This patch allows exp not to be removed by setting IPS_CONFIRMED
in the status of the tmpl.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/3fa58a6fbd1e9e5682d09cdafb08fba004cb12ec
- https://git.kernel.org/stable/c/4914109a8e1e494c6aa9852f9e84ec77a5fc643f
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://seadragnol.github.io/posts/CVE-2023-52927/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52927.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52927
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
