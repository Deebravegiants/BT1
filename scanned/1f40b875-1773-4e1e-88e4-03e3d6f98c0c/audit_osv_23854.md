# [M] ip: Fix data-races around sysctl_ip_prot_sock.

## Summary
Severity: Medium
Advisory: CVE-2022-49578
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49578
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

ip: Fix data-races around sysctl_ip_prot_sock.

sysctl_ip_prot_sock is accessed concurrently, and there is always a chance
of data-race.  So, all readers and writers need some basic protection to
avoid load/store-tearing.

## References
- https://git.kernel.org/stable/c/95724fe897a4ecf2be51452ef96e818568071664
- https://git.kernel.org/stable/c/9add240f76af6d141d2eebd3a1558a0e503a993d
- https://git.kernel.org/stable/c/9b55c20f83369dd54541d9ddbe3a018a8377f451
- https://git.kernel.org/stable/c/ef699813d99cc29e6e25c9f6da7766526cc8bd6e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49578.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49578
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
