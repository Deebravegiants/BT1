# [H] net/ip6_tunnel: Prevent perpetual tunnel growth

## Summary
Severity: High
Advisory: CVE-2025-40173
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40173
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.196, >=5.16.0 <6.1.158, >=6.2.0 <6.6.114, >=6.7.0 <6.12.55, >=6.13.0 <6.17.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/ip6_tunnel: Prevent perpetual tunnel growth

Similarly to ipv4 tunnel, ipv6 version updates dev->needed_headroom, too.
While ipv4 tunnel headroom adjustment growth was limited in
commit 5ae1e9922bbd ("net: ip_tunnel: prevent perpetual headroom growth"),
ipv6 tunnel yet increases the headroom without any ceiling.

Reflect ipv4 tunnel headroom adjustment limit on ipv6 version.

Credits to Francesco Ruggeri, who was originally debugging this issue
and wrote local Arista-specific patch and a reproducer.

## References
- https://git.kernel.org/stable/c/10fe967efe73c610e526ff7460581610633dee9c
- https://git.kernel.org/stable/c/11f6066af3bfb8149aa16c42c0b0c5ea5b199a94
- https://git.kernel.org/stable/c/21f4d45eba0b2dcae5dbc9e5e0ad08735c993f16
- https://git.kernel.org/stable/c/402b6985e872b4cf394bbbf33b503947a326a6cb
- https://git.kernel.org/stable/c/48294a67863c9cfa367abb66bbf0ef6548ae124f
- https://git.kernel.org/stable/c/566f8d5c8a443f2dd69c5460fdec43ed1c870c65
- https://git.kernel.org/stable/c/b6eb25d870f1a8ae571fd3da2244b71df547824b
- https://git.kernel.org/stable/c/eeb4345488672584db4f8c20a1ae13a212ce31c4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40173.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40173
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
