# [H] CVE-2020-36791

## Summary
Severity: High
Advisory: CVE-2020-36791
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-05-07
Source: https://osv.dev/vulnerability/CVE-2020-36791
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net_sched: keep alloc_hash updated after hash allocation

In commit 599be01ee567 ("net_sched: fix an OOB access in cls_tcindex")
I moved cp->hash calculation before the first
tcindex_alloc_perfect_hash(), but cp->alloc_hash is left untouched.
This difference could lead to another out of bound access.

cp->alloc_hash should always be the size allocated, we should
update it after this tcindex_alloc_perfect_hash().

## References
- https://blog.cdthoughts.ch/2021/03/16/syzbot-bug.html
- https://syzkaller.appspot.com/bug?id=ea260693da894e7b078d18fca2c9c0a19b457534
- https://git.kernel.org/stable/c/0d1c3530e1bd38382edef72591b78e877e0edcd3
- https://git.kernel.org/stable/c/557d015ffb27b672e24e6ad141fd887783871dc2
- https://git.kernel.org/stable/c/c4453d2833671e3a9f6bd52f0f581056c3736386
- https://git.kernel.org/stable/c/d23faf32e577922b6da20bf3740625c1105381bf
- https://git.kernel.org/stable/c/d6cdc5bb19b595486fb2e6661e5138d73a57f454
- https://git.kernel.org/stable/c/9f8b6c44be178c2498a00b270872a6e30e7c8266
- https://git.kernel.org/stable/c/bd3ee8fb6371b45c71c9345cc359b94da2ddefa9
