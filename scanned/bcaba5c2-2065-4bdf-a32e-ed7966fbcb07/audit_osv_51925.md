# [H] CVE-2021-45485

## Summary
Severity: High
Advisory: CVE-2021-45485
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-12-25
Source: https://osv.dev/vulnerability/CVE-2021-45485
Type: osv

## Details
In the IPv6 implementation in the Linux kernel before 5.13.3, net/ipv6/output_core.c has an information leak because of certain use of a hash table which, although big, doesn't properly consider that IPv6-based attackers can typically choose among many IPv6 source addresses.

## References
- https://arxiv.org/pdf/2112.09604.pdf
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.3
- https://security.netapp.com/advisory/ntap-20220121-0001/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=62f20e068ccc50d6ab66fdb72ba90da2b9418c99
- https://www.oracle.com/security-alerts/cpujul2022.html
