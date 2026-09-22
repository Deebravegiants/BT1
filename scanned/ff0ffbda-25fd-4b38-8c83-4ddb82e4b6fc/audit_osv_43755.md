# [H] net/atm: fix slab-out-of-bounds read in vcc_setsockopt()

## Summary
Severity: High
Advisory: CVE-2026-74689
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74689
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/atm: fix slab-out-of-bounds read in vcc_setsockopt()

vcc_setsockopt() contained an ineffective optlen check:
  if (__SO_LEVEL_MATCH(optname, level) && optlen != __SO_SIZE(optname))
      return -EINVAL;

If __SO_LEVEL_MATCH(optname, level) evaluated to false (e.g. if the caller
passed a mismatched level), the length check optlen != __SO_SIZE(optname)
was short-circuited and bypassed. Execution then fell through to switch(optname),
calling copy_from_sockptr() assuming optval contained sufficient space.

Furthermore, even if level matched, a cgroup BPF setsockopt filter could shrink
optlen after entry. Because copy_from_sockptr() on kernel pointers uses memcpy(),
this leads to a KASAN slab-out-of-bounds read when optlen is smaller than the
expected structure size.

Fix this by using copy_safe_from_sockptr(), which unconditionally validates
that optlen is at least the expected size before copying. Also change the local
'value' variable type from 'unsigned long' to 'int' so that SO_SETCLP matches
its sizeof(int) ABI encoding on 64-bit systems.

## References
- https://git.kernel.org/stable/c/2c5988c7349c0b64a7e0441bfc6e1dca54f7116a
- https://git.kernel.org/stable/c/35f258fee9ed358c6d0f57f91c30bf029c3724af
- https://git.kernel.org/stable/c/6eb6af88710977eb529b558a07294874d8c40c4d
- https://git.kernel.org/stable/c/9f77c1ab382188f5b51982fab6d913443b6dc59f
- https://git.kernel.org/stable/c/b3bcd5d65ac03c15787b2a5b36c718e26a689336
- https://git.kernel.org/stable/c/d0c80dbb970439bd2eeb0e5effff8c16a5f4e1e3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74689.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74689
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
