# [H] drm/vmwgfx: Prevent unmapping active read buffers

## Summary
Severity: High
Advisory: CVE-2024-46710
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-13
Source: https://osv.dev/vulnerability/CVE-2024-46710
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vmwgfx: Prevent unmapping active read buffers

The kms paths keep a persistent map active to read and compare the cursor
buffer. These maps can race with each other in simple scenario where:
a) buffer "a" mapped for update
b) buffer "a" mapped for compare
c) do the compare
d) unmap "a" for compare
e) update the cursor
f) unmap "a" for update
At step "e" the buffer has been unmapped and the read contents is bogus.

Prevent unmapping of active read buffers by simply keeping a count of
how many paths have currently active maps and unmap only when the count
reaches 0.

## References
- https://git.kernel.org/stable/c/0851b1ec650adadcaa23ec96daad95a55bf966f0
- https://git.kernel.org/stable/c/58a3714db4d9dcaeb9fc4905141e17b9f536c0a5
- https://git.kernel.org/stable/c/aba07b9a0587f50e5d3346eaa19019cf3f86c0ea
- https://git.kernel.org/stable/c/d5228d158e4c0b1663b3983044913c15c3d0135e
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46710.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46710
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
