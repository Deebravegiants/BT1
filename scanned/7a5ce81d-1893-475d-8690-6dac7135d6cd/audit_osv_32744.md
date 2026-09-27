# [H] riscv: uprobes: Add missing fence.i after building the XOL buffer

## Summary
Severity: High
Advisory: CVE-2025-37822
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-08
Source: https://osv.dev/vulnerability/CVE-2025-37822
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.200, >=5.16.0 <6.1.163, >=6.2.0 <6.6.121, >=6.7.0 <6.12.26, >=6.13.0 <6.14.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

riscv: uprobes: Add missing fence.i after building the XOL buffer

The XOL (execute out-of-line) buffer is used to single-step the
replaced instruction(s) for uprobes. The RISC-V port was missing a
proper fence.i (i$ flushing) after constructing the XOL buffer, which
can result in incorrect execution of stale/broken instructions.

This was found running the BPF selftests "test_progs:
uprobe_autoattach, attach_probe" on the Spacemit K1/X60, where the
uprobes tests randomly blew up.

## References
- https://git.kernel.org/stable/c/1dbb95a36499374c51b47ee8ae258a8862c20978
- https://git.kernel.org/stable/c/77c956152a3a7c7a18b68f3654f70565b2181d03
- https://git.kernel.org/stable/c/7d1d19a11cfbfd8bae1d89cc010b2cc397cd0c48
- https://git.kernel.org/stable/c/b6d8d4d01ca8514fa89b05355f296758a91e2297
- https://git.kernel.org/stable/c/bcf6d3158c5902d92b6d62335af4422b7bf7c4e2
- https://git.kernel.org/stable/c/be6d98766ac952d38241d5a5b213f363afa421c3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37822.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37822
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
