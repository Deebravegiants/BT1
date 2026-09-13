# [H] btrfs: fix iteration of extrefs during log replay

## Summary
Severity: High
Advisory: CVE-2025-38382
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38382
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.144, >=6.2.0 <6.12.37, >=6.7.0 <6.15.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix iteration of extrefs during log replay

At __inode_add_ref() when processing extrefs, if we jump into the next
label we have an undefined value of victim_name.len, since we haven't
initialized it before we did the goto. This results in an invalid memory
access in the next iteration of the loop since victim_name.len was not
initialized to the length of the name of the current extref.

Fix this by initializing victim_name.len with the current extref's name
length.

## References
- https://git.kernel.org/stable/c/2d11d274e2e1d7c79e2ca8461ce3ff3a95c11171
- https://git.kernel.org/stable/c/539969fc472886a1d63565459514d47e27fef461
- https://git.kernel.org/stable/c/54a7081ed168b72a8a2d6ef4ba3a1259705a2926
- https://git.kernel.org/stable/c/7ac790dc2ba00499a8d671d4a24de4d4ad27e234
- https://git.kernel.org/stable/c/aee57a0293dca675637e5504709f9f8fd8e871be
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38382.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38382
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
