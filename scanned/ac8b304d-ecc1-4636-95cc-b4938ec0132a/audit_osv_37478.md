# [H] net: ipv6: flowlabel: defer exclusive option free until RCU teardown

## Summary
Severity: High
Advisory: CVE-2026-31680
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-25
Source: https://osv.dev/vulnerability/CVE-2026-31680
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ipv6: flowlabel: defer exclusive option free until RCU teardown

`ip6fl_seq_show()` walks the global flowlabel hash under the seq-file
RCU read-side lock and prints `fl->opt->opt_nflen` when an option block
is present.

Exclusive flowlabels currently free `fl->opt` as soon as `fl->users`
drops to zero in `fl_release()`. However, the surrounding
`struct ip6_flowlabel` remains visible in the global hash table until
later garbage collection removes it and `fl_free_rcu()` finally tears it
down.

A concurrent `/proc/net/ip6_flowlabel` reader can therefore race that
early `kfree()` and dereference freed option state, triggering a crash
in `ip6fl_seq_show()`.

Fix this by keeping `fl->opt` alive until `fl_free_rcu()`. That matches
the lifetime already required for the enclosing flowlabel while readers
can still reach it under RCU.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/3c54b66c83fb8fcbde8e6a7bf90b65856e39f827
- https://git.kernel.org/stable/c/414726b69921fe6355ae453f5b35e68dd078342a
- https://git.kernel.org/stable/c/4b6798024f7b2d535f3db1002c760143cdbd1bd3
- https://git.kernel.org/stable/c/572ce62778519a7d4d1c15f55dd2e45a474133c4
- https://git.kernel.org/stable/c/5a6b15f861b7c1304949e3350d23490a5fe429fd
- https://git.kernel.org/stable/c/6c7fbdb8ffde6413640de7cfbd7c976c353e89f8
- https://git.kernel.org/stable/c/8027964931785cb73d520ac70a342a3dc16c249b
- https://git.kernel.org/stable/c/9ca562bb8e66978b53028fa32b1a190708e6a091
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31680.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31680
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
