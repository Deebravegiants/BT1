# [H] media: s5p-jpeg: prevent buffer overflows

## Summary
Severity: High
Advisory: CVE-2024-53061
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53061
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <4.19.324, >=4.20.0 <5.4.286, >=5.5.0 <5.10.230, >=5.11.0 <5.15.172, >=5.16.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: s5p-jpeg: prevent buffer overflows

The current logic allows word to be less than 2. If this happens,
there will be buffer overflows, as reported by smatch. Add extra
checks to prevent it.

While here, remove an unused word = 0 assignment.

## References
- https://git.kernel.org/stable/c/14a22762c3daeac59a5a534e124acbb4d7a79b3a
- https://git.kernel.org/stable/c/784bc785a453eb2f8433dd62075befdfa1b2d6fd
- https://git.kernel.org/stable/c/a930cddfd153b5d4401df0c01effa14c831ff21e
- https://git.kernel.org/stable/c/c5f6fefcda8fac8f082b6c5bf416567f4e100c51
- https://git.kernel.org/stable/c/c85db2d4432de4ff9d97006691ce2dcb5bda660e
- https://git.kernel.org/stable/c/c951a0859fdacf49a2298b5551a7e52b95ff6f51
- https://git.kernel.org/stable/c/e5117f6e7adcf9fd7546cdd0edc9abe4474bc98b
- https://git.kernel.org/stable/c/f54e8e1e39dacccebcfb9a9a36f0552a0a97e2ef
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53061.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53061
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
