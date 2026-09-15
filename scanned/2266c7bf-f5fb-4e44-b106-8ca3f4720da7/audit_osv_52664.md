# [M] CVE-2022-0286

## Summary
Severity: Medium
Advisory: CVE-2022-0286
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-31
Source: https://osv.dev/vulnerability/CVE-2022-0286
Type: osv

## Details
A flaw was found in the Linux kernel. A null pointer dereference in bond_ipsec_add_sa() may lead to local denial of service.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=105cd17a866017b45f3c45901b394c711c97bf40
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://syzkaller.appspot.com/bug?id=160f641886d88bf11cbf1236cc4db994bb210626
