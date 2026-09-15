# [M] amt: fix memory leak for advertisement message

## Summary
Severity: Medium
Advisory: CVE-2022-49461
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49461
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

amt: fix memory leak for advertisement message

When a gateway receives an advertisement message, it extracts relay
information and then it should be freed.
But the advertisement handler doesn't free it.
So, memory leak would occur.

## References
- https://git.kernel.org/stable/c/19bb2d57eac86a368839a92117d8a10ab7183623
- https://git.kernel.org/stable/c/e7322da399fb86a2072f008b56f7160afa1b2051
- https://git.kernel.org/stable/c/fe29794c3585d039fefebaa2b5a4932a627ad4fd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49461.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49461
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
