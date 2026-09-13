# [H] wifi: mt76: fix linked list corruption

## Summary
Severity: High
Advisory: CVE-2025-39918
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39918
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.46, >=6.13.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mt76: fix linked list corruption

Never leave scheduled wcid entries on the temporary on-stack list

## References
- https://git.kernel.org/stable/c/49fba87205bec14a0f6bd997635bf3968408161e
- https://git.kernel.org/stable/c/c91a59b04f928cb4a1436b0e0a27650883d0388a
- https://git.kernel.org/stable/c/e4d5a5fc61fdc65220a1ce078d24c1d20bbb0835
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39918.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39918
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
