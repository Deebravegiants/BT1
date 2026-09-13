# [H] bcachefs: Check for journal entries overruning end of sb clean section

## Summary
Severity: High
Advisory: CVE-2024-35948
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-35948
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

bcachefs: Check for journal entries overruning end of sb clean section

Fix a missing bounds check in superblock validation.

Note that we don't yet have repair code for this case - repair code for
individual items is generally low priority, since the whole superblock
is checksummed, validated prior to write, and we have backups.

## References
- https://git.kernel.org/stable/c/fcdbc1d7a4b638e5d5668de461f320386f3002aa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35948.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35948
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
