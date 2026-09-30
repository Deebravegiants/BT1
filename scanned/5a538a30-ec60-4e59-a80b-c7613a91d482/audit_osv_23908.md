# [H] srcu: Tighten cleanup_srcu_struct() GP checks

## Summary
Severity: High
Advisory: CVE-2022-49651
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49651
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.18.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

srcu: Tighten cleanup_srcu_struct() GP checks

Currently, cleanup_srcu_struct() checks for a grace period in progress,
but it does not check for a grace period that has not yet started but
which might start at any time.  Such a situation could result in a
use-after-free bug, so this commit adds a check for a grace period that
is needed but not yet started to cleanup_srcu_struct().

## References
- https://git.kernel.org/stable/c/8ed00760203d8018bee042fbfe8e076579be2c2b
- https://git.kernel.org/stable/c/e997dda6502eefbc1032d6b0da7b353c53344b07
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49651.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49651
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
