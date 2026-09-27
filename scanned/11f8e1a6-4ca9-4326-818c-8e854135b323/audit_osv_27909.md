# [H] dm-crypt: don't modify the data when using authenticated encryption

## Summary
Severity: High
Advisory: CVE-2024-26763
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26763
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <4.19.308, >=4.20.0 <5.4.270, >=5.5.0 <5.10.211, >=5.11.0 <5.15.150, >=5.16.0 <6.1.80, >=6.2.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm-crypt: don't modify the data when using authenticated encryption

It was said that authenticated encryption could produce invalid tag when
the data that is being encrypted is modified [1]. So, fix this problem by
copying the data into the clone bio first and then encrypt them inside the
clone bio.

This may reduce performance, but it is needed to prevent the user from
corrupting the device by writing data with O_DIRECT and modifying them at
the same time.

[1] https://lore.kernel.org/all/20240207004723.GA35324@sol.localdomain/T/

## References
- https://git.kernel.org/stable/c/0dccbb93538fe89a86c6de31d4b1c8c560848eaa
- https://git.kernel.org/stable/c/1a4371db68a31076afbe56ecce34fbbe6c80c529
- https://git.kernel.org/stable/c/3c652f6fa1e1f9f02c3fbf359d260ad153ec5f90
- https://git.kernel.org/stable/c/43a202bd552976497474ae144942e32cc5f34d7e
- https://git.kernel.org/stable/c/50c70240097ce41fe6bce6478b80478281e4d0f7
- https://git.kernel.org/stable/c/64ba01a365980755732972523600a961c4266b75
- https://git.kernel.org/stable/c/d9e3763a505e50ba3bd22846f2a8db99429fb857
- https://git.kernel.org/stable/c/e08c2a8d27e989f0f5b0888792643027d7e691e6
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26763.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26763
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
