# [M] net: tipc: fix possible refcount leak in tipc_sk_create()

## Summary
Severity: Medium
Advisory: CVE-2022-49620
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49620
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <4.9.324, >=4.10.0 <4.14.289, >=4.15.0 <4.19.253, >=4.20.0 <5.4.207, >=5.5.0 <5.10.132, >=5.11.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: tipc: fix possible refcount leak in tipc_sk_create()

Free sk in case tipc_sk_insert() fails.

## References
- https://git.kernel.org/stable/c/00aff3590fc0a73bddd3b743863c14e76fd35c0c
- https://git.kernel.org/stable/c/3b2957fc09fe1ac7f07f40dd50dd5f93e3f3a7a2
- https://git.kernel.org/stable/c/4919d82f7041157a421ca9bf39a78551d5ad8a1b
- https://git.kernel.org/stable/c/638fa20b618b2bbcf86da71231624cc82121a036
- https://git.kernel.org/stable/c/7bc9e7f70bc57d8f02ffea2a42094281effb15ef
- https://git.kernel.org/stable/c/833ecd0eae76eadf81d6d747bb5bc992d1151867
- https://git.kernel.org/stable/c/ef488669b2652bde5b6ee5a409a5b048a2a50db4
- https://git.kernel.org/stable/c/efa78f2ae363428525fb4981bb63c555ee79f3c7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49620.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49620
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
