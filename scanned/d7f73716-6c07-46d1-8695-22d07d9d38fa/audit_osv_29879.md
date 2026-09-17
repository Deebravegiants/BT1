# [C] net/smc: check smcd_v2_ext_offset when receiving proposal msg

## Summary
Severity: Critical
Advisory: CVE-2024-47408
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-47408
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.15.176, >=5.16.0 <6.1.122, >=6.2.0 <6.6.68, >=6.7.0 <6.12.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: check smcd_v2_ext_offset when receiving proposal msg

When receiving proposal msg in server, the field smcd_v2_ext_offset in
proposal msg is from the remote client and can not be fully trusted.
Once the value of smcd_v2_ext_offset exceed the max value, there has
the chance to access wrong address, and crash may happen.

This patch checks the value of smcd_v2_ext_offset before using it.

## References
- https://git.kernel.org/stable/c/48d5a8a304a643613dab376a278f29d3e22f7c34
- https://git.kernel.org/stable/c/935caf324b445fe73d7708fae6f7176fb243f357
- https://git.kernel.org/stable/c/9ab332deb671d8f7e66d82a2ff2b3f715bc3a4ad
- https://git.kernel.org/stable/c/a36364d8d4fabb105001f992fb8ff2d3546203d6
- https://git.kernel.org/stable/c/e1cc8be2a785a8f1ce1f597f3e608602c5fccd46
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47408.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47408
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
