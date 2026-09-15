# [H] ipv4: icmp: fix null-ptr-deref in icmp_build_probe()

## Summary
Severity: High
Advisory: CVE-2026-43099
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43099
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv4: icmp: fix null-ptr-deref in icmp_build_probe()

ipv6_stub->ipv6_dev_find() may return ERR_PTR(-EAFNOSUPPORT) when the
IPv6 stack is not active (CONFIG_IPV6=m and not loaded), and passing
this error pointer to dev_hold() will cause a kernel crash with
null-ptr-deref.

Instead, silently discard the request. RFC 8335 does not appear to
define a specific response for the case where an IPv6 interface
identifier is syntactically valid but the implementation cannot perform
the lookup at runtime, and silently dropping the request may safer than
misreporting "No Such Interface".

## References
- https://git.kernel.org/stable/c/0f21bc261e60f0c696c58841c4873ff77ed83673
- https://git.kernel.org/stable/c/47a8bf52156ac7e7a581eca31c1f964ba4258d4d
- https://git.kernel.org/stable/c/5b9911582d441f72fe6ccb15ffe3303bbc07f6f5
- https://git.kernel.org/stable/c/6be325206850a0891896d38bcf83a09d8b54ec48
- https://git.kernel.org/stable/c/dc5db4db19766a61ad65d81d1f55b1c1e51ba78d
- https://git.kernel.org/stable/c/f91b3ed9e7fa82a70511b5f6901c88379acf2964
- https://git.kernel.org/stable/c/fde29fd9349327acc50d19a0b5f3d5a6c964dfd8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43099.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43099
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
