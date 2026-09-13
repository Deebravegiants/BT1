# [H] objtool, nvmet: Fix out-of-bounds stack access in nvmet_ctrl_state_show()

## Summary
Severity: High
Advisory: CVE-2025-39778
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-39778
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

objtool, nvmet: Fix out-of-bounds stack access in nvmet_ctrl_state_show()

The csts_state_names[] array only has six sparse entries, but the
iteration code in nvmet_ctrl_state_show() iterates seven, resulting in a
potential out-of-bounds stack read.  Fix that.

Fixes the following warning with an UBSAN kernel:

  vmlinux.o: warning: objtool: .text.nvmet_ctrl_state_show: unexpected end of section

## References
- https://git.kernel.org/stable/c/0cc0efc58d6c741b2868d4af24874d7fec28a575
- https://git.kernel.org/stable/c/107a23185d990e3df6638d9a84c835f963fe30a6
- https://git.kernel.org/stable/c/1adc93a525fdee8e2b311e6d5fd93eb69714ca05
- https://git.kernel.org/stable/c/8fbf37a3577b4d64c150cafde338eee17b2f2ea4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39778.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39778
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
