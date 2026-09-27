# [H] regulator: gpio: Fix the out-of-bounds access to drvdata::gpiods

## Summary
Severity: High
Advisory: CVE-2025-38395
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38395
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.296, >=5.5.0 <5.10.240, >=5.11.0 <5.15.187, >=5.16.0 <6.1.144, >=6.2.0 <6.6.97, >=6.7.0 <6.12.37, >=6.13.0 <6.15.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

regulator: gpio: Fix the out-of-bounds access to drvdata::gpiods

drvdata::gpiods is supposed to hold an array of 'gpio_desc' pointers. But
the memory is allocated for only one pointer. This will lead to
out-of-bounds access later in the code if 'config::ngpios' is > 1. So
fix the code to allocate enough memory to hold 'config::ngpios' of GPIO
descriptors.

While at it, also move the check for memory allocation failure to be below
the allocation to make it more readable.

## References
- https://git.kernel.org/stable/c/24418bc77a66cb5be9f5a837431ba3674ed8b52f
- https://git.kernel.org/stable/c/3830ab97cda9599872625cc0dc7b00160193634f
- https://git.kernel.org/stable/c/56738cbac3bbb1d39a71a07f57484dec1db8b239
- https://git.kernel.org/stable/c/9fe71972869faed1f8f9b3beb9040f9c1b300c79
- https://git.kernel.org/stable/c/a1e12fac214d4f49fcb186dbdf9c5592e7fa0a7a
- https://git.kernel.org/stable/c/a3cd5ae7befbac849e0e0529c94ca04e8093cfd2
- https://git.kernel.org/stable/c/c9764fd88bc744592b0604ccb6b6fc1a5f76b4e3
- https://git.kernel.org/stable/c/e4d19e5d71b217940e33f2ef6c6962b7b68c5606
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38395.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38395
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
