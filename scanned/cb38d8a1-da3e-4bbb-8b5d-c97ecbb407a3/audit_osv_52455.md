# [M] CVE-2021-47466

## Summary
Severity: Medium
Advisory: CVE-2021-47466
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47466
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm, slub: fix potential memoryleak in kmem_cache_open()

In error path, the random_seq of slub cache might be leaked.  Fix this
by using __kmem_cache_release() to release all the relevant resources.

## References
- https://git.kernel.org/stable/c/42b81946e3ac9ea0372ba16e05160dc11e02694f
- https://git.kernel.org/stable/c/4f5d1c29cfab5cb0ab885059818751bdef32e2bb
- https://git.kernel.org/stable/c/568f906340b43120abd6fcc67c37396482f85930
- https://git.kernel.org/stable/c/9037c57681d25e4dcc442d940d6dbe24dd31f461
