# [M] CVE-2018-19854

## Summary
Severity: Medium
Advisory: CVE-2018-19854
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-12-04
Source: https://osv.dev/vulnerability/CVE-2018-19854
Type: osv

## Details
An issue was discovered in the Linux kernel before 4.19.3. crypto_report_one() and related functions in crypto/crypto_user.c (the crypto user configuration API) do not fully initialize structures that are copied to userspace, potentially leaking sensitive memory to user programs. NOTE: this is a CVE-2013-2547 regression but with easier exploitability because the attacker does not need a capability (however, the system must have the CONFIG_CRYPTO_USER kconfig option).

## References
- https://access.redhat.com/errata/RHSA-2019:3309
- https://access.redhat.com/errata/RHSA-2019:3517
- https://kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.19.3
- https://usn.ubuntu.com/3872-1/
- https://usn.ubuntu.com/3878-1/
- https://usn.ubuntu.com/3878-2/
- https://usn.ubuntu.com/3901-1/
- https://usn.ubuntu.com/3901-2/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=f43f39958beb206b53292801e216d9b8a660f087
- https://github.com/torvalds/linux/commit/f43f39958beb206b53292801e216d9b8a660f087
