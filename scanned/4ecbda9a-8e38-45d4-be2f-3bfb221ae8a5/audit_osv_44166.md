# [H] xfs: avoid UAF on sc->tempip in xrep_tempfile_create

## Summary
Severity: High
Advisory: CVE-2026-80531
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80531
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfs: avoid UAF on sc->tempip in xrep_tempfile_create

LOLLM noticed a potential UAF if the tempfile creation code fails after
it set sc->tempip.  Fix that.

## References
- https://git.kernel.org/stable/c/08a20776ce33a2a52d856911e447c59424f0465a
- https://git.kernel.org/stable/c/0c88e10d12de9ca7cbed1467bb1b52310101bff8
- https://git.kernel.org/stable/c/96246a3200d32a43766152e56bc7ae2d93604d74
- https://git.kernel.org/stable/c/cd1f876d1bc2e94f271e07c606cacd85b109108a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80531.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80531
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
