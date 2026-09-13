# [H] iomap: add a separate bio_set for iomap_split_ioend

## Summary
Severity: High
Advisory: CVE-2026-80720
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80720
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

iomap: add a separate bio_set for iomap_split_ioend

iomap_split_ioend can split bios that already come from
iomap_ioend_bioset and thus deadlock when the bioset is exhausted.

Add a separate bio_set to avoid this deadlock.

Christian Brauner <brauner@kernel.org> says:
Mark iomap_ioend_split_bioset static as it is only used in ioend.c,
fixing the sparse warning reported by the kernel test robot.

## References
- https://git.kernel.org/stable/c/4a869be56e9f6ce7462abcf324ebdefc5de051be
- https://git.kernel.org/stable/c/c679ce3be6cb63763d68ab9b5d9d73ddc0a40762
- https://git.kernel.org/stable/c/cfc686a1174aa904dcad9b9a7c5e46b484d27e4e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80720.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80720
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
