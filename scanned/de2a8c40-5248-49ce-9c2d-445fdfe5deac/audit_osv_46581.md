# [M] CVE-2013-7470

## Summary
Severity: Medium
Advisory: CVE-2013-7470
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-23
Source: https://osv.dev/vulnerability/CVE-2013-7470
Type: osv

## Details
cipso_v4_validate in include/net/cipso_ipv4.h in the Linux kernel before 3.11.7, when CONFIG_NETLABEL is disabled, allows attackers to cause a denial of service (infinite loop and crash), as demonstrated by icmpsic, a different vulnerability than CVE-2013-0310.

## References
- https://cdn.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.11.7
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=f2e5ddcc0d12f9c4c7b254358ad245c9dddce13b
- https://github.com/torvalds/linux/commit/f2e5ddcc0d12f9c4c7b254358ad245c9dddce13b
- https://www.arista.com/en/support/advisories-notices/security-advisories/7098-security-advisory-40
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=f2e5ddcc0d12f9c4c7b254358ad245c9dddce13b
- https://github.com/torvalds/linux/commit/f2e5ddcc0d12f9c4c7b254358ad245c9dddce13b
- https://support.f5.com/csp/article/K21914362
