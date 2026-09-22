# [H] wifi: rtw89: pci: validate release report content before using for RTL8922DE

## Summary
Severity: High
Advisory: CVE-2026-43176
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43176
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: rtw89: pci: validate release report content before using for RTL8922DE

The commit 957eda596c76
("wifi: rtw89: pci: validate sequence number of TX release report")
does validation on existing chips, which somehow a release report of SKB
becomes malformed. As no clear cause found, add rules ahead for RTL8922DE
to avoid crash if it happens.

## References
- https://git.kernel.org/stable/c/3e8a88b5e8b3506d9c5e031a65ba65ce9a0683a3
- https://git.kernel.org/stable/c/5f93d611b33a05bd03d6843c8efe8cb6a1992620
- https://git.kernel.org/stable/c/ebeaa3b24ba568ff8505165f954dba15cc53e4b3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43176.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43176
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
