# [H] net: explicitly clear the sk pointer, when pf->create fails

## Summary
Severity: High
Advisory: CVE-2024-50186
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50186
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.57, >=6.7.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: explicitly clear the sk pointer, when pf->create fails

We have recently noticed the exact same KASAN splat as in commit
6cd4a78d962b ("net: do not leave a dangling sk pointer, when socket
creation fails"). The problem is that commit did not fully address the
problem, as some pf->create implementations do not use sk_common_release
in their error paths.

For example, we can use the same reproducer as in the above commit, but
changing ping to arping. arping uses AF_PACKET socket and if packet_create
fails, it will just sk_free the allocated sk object.

While we could chase all the pf->create implementations and make sure they
NULL the freed sk object on error from the socket, we can't guarantee
future protocols will not make the same mistake.

So it is easier to just explicitly NULL the sk pointer upon return from
pf->create in __sock_create. We do know that pf->create always releases the
allocated sk object on error, so if the pointer is not NULL, it is
definitely dangling.

## References
- https://git.kernel.org/stable/c/563e6892e21d6ecabdf62103fc4e7b326d212334
- https://git.kernel.org/stable/c/631083143315d1b192bd7d915b967b37819e88ea
- https://git.kernel.org/stable/c/8e1b72fd74bf9da3b099d09857f4e7f114f38e12
- https://git.kernel.org/stable/c/b7d22a79ff4e962b8af5ffe623abd1d6c179eb9f
- https://git.kernel.org/stable/c/daf462ff3cde6ecf22b98d9ae770232c10d28de2
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50186.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50186
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
