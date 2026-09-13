# [H] netfilter: nf_tables: mark set as dead when unbinding anonymous set with timeout

## Summary
Severity: High
Advisory: CVE-2024-26643
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-21
Source: https://osv.dev/vulnerability/CVE-2024-26643
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.5.0 <6.7.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: mark set as dead when unbinding anonymous set with timeout

While the rhashtable set gc runs asynchronously, a race allows it to
collect elements from anonymous sets with timeouts while it is being
released from the commit path.

Mingi Cho originally reported this issue in a different path in 6.1.x
with a pipapo set with low timeouts which is not possible upstream since
7395dfacfff6 ("netfilter: nf_tables: use timestamp to check for set
element timeout").

Fix this by setting on the dead flag for anonymous sets to skip async gc
in this case.

According to 08e4c8c5919f ("netfilter: nf_tables: mark newset as dead on
transaction abort"), Florian plans to accelerate abort path by releasing
objects via workqueue, therefore, this sets on the dead flag for abort
path too.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/291cca35818bd52a407bc37ab45a15816039e363
- https://git.kernel.org/stable/c/406b0241d0eb598a0b330ab20ae325537d8d8163
- https://git.kernel.org/stable/c/5224afbc30c3ca9ba23e752f0f138729b2c48dd8
- https://git.kernel.org/stable/c/552705a3650bbf46a22b1adedc1b04181490fc36
- https://git.kernel.org/stable/c/b2d6f9a5b1cf968f1eaa71085ceeb09c2cb276b1
- https://git.kernel.org/stable/c/d75a589bb92af1abf3b779cfcd1977ca11b27033
- https://git.kernel.org/stable/c/e2d45f467096e931044f0ab7634499879d851a5c
- https://git.kernel.org/stable/c/edcf1a3f182ecf8b6b805f0ce90570ea98c5f6bf
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26643.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26643
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
