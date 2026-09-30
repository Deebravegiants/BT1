# [H] staging: rtl8712: fix use after free bugs

## Summary
Severity: High
Advisory: CVE-2022-49956
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-49956
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.37 <4.9.328, >=4.10.0 <4.14.293, >=4.15.0 <4.19.258, >=4.20.0 <5.4.213, >=5.5.0 <5.10.142, >=5.11.0 <5.15.66, >=5.16.0 <5.19.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: rtl8712: fix use after free bugs

_Read/Write_MACREG callbacks are NULL so the read/write_macreg_hdl()
functions don't do anything except free the "pcmd" pointer.  It
results in a use after free.  Delete them.

## References
- https://git.kernel.org/stable/c/19e3f69d19801940abc2ac37c169882769ed9770
- https://git.kernel.org/stable/c/376e15487fec837301d888068a3fcc82efb6171a
- https://git.kernel.org/stable/c/7dce6b0ee7d78667d6c831ced957a08769973063
- https://git.kernel.org/stable/c/9fd6170c5e2d0ccd027abe26f6f5ffc528e1bb27
- https://git.kernel.org/stable/c/b1727def850904e4b8ba384043775672841663a1
- https://git.kernel.org/stable/c/d0aac7146e96bf39e79c65087d21dfa02ef8db38
- https://git.kernel.org/stable/c/dc02aaf950015850e7589696521c7fca767cea77
- https://git.kernel.org/stable/c/e230a4455ac3e9b112f0367d1b8e255e141afae0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49956.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49956
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
