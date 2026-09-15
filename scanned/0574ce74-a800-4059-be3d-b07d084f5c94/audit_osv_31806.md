# [H] net: xdp: Disallow attaching device-bound programs in generic mode

## Summary
Severity: High
Advisory: CVE-2025-21808
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21808
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: xdp: Disallow attaching device-bound programs in generic mode

Device-bound programs are used to support RX metadata kfuncs. These
kfuncs are driver-specific and rely on the driver context to read the
metadata. This means they can't work in generic XDP mode. However, there
is no check to disallow such programs from being attached in generic
mode, in which case the metadata kfuncs will be called in an invalid
context, leading to crashes.

Fix this by adding a check to disallow attaching device-bound programs
in generic mode.

## References
- https://git.kernel.org/stable/c/3595599fa8360bb3c7afa7ee50c810b4a64106ea
- https://git.kernel.org/stable/c/557707906dd3e34b8a8c265f664d19f95799937e
- https://git.kernel.org/stable/c/5a9eae683d6c36e8a7aa31e5eb8b369e41aa66e1
- https://git.kernel.org/stable/c/b1bc4a35a04cbeb85b6ef5911ec015baa424989f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21808.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21808
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
