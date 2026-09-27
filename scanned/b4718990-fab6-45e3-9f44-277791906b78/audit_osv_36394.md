# [H] netfilter: xt_CT: drop pending enqueued packets on template removal

## Summary
Severity: High
Advisory: CVE-2026-23391
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-23391
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.4.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: xt_CT: drop pending enqueued packets on template removal

Templates refer to objects that can go away while packets are sitting in
nfqueue refer to:

- helper, this can be an issue on module removal.
- timeout policy, nfnetlink_cttimeout might remove it.

The use of templates with zone and event cache filter are safe, since
this just copies values.

Flush these enqueued packets in case the template rule gets removed.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/19a230dec6bb8928e3f96387f9085cf2c79bcef9
- https://git.kernel.org/stable/c/55445134d42b84cb0a272e42c98d233ca65eca83
- https://git.kernel.org/stable/c/63b8097cea1923fe82cd598068d0796da8c015ec
- https://git.kernel.org/stable/c/777d02efe3d630cca4c1b63962cec17c57711325
- https://git.kernel.org/stable/c/cb549925875fa06dd155e49db4ac2c5044c30f9c
- https://git.kernel.org/stable/c/cc57506dd66555899560b9c0f24e813f034e12ec
- https://git.kernel.org/stable/c/d2d0bae0c9a2a17b6990a2966f5cdce0813d6256
- https://git.kernel.org/stable/c/f62a218a946b19bb59abdd5361da85fa4606b96b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23391.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23391
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
