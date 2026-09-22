# [M] CVE-2020-36311

## Summary
Severity: Medium
Advisory: CVE-2020-36311
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-07
Source: https://osv.dev/vulnerability/CVE-2020-36311
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.9. arch/x86/kvm/svm/sev.c allows attackers to cause a denial of service (soft lockup) by triggering destruction of a large SEV VM (which requires unregistering many encrypted regions), aka CID-7be74942f184.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.9
- https://lists.debian.org/debian-lts-announce/2021/07/msg00015.html
- https://www.debian.org/security/2021/dsa-4941
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=7be74942f184fdfba34ddd19a0d995deb34d4a03
