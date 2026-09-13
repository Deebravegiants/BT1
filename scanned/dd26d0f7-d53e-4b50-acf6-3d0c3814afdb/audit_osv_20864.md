# [M] CVE-2021-3772

## Summary
Severity: Medium
Advisory: CVE-2021-3772
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2022-03-02
Source: https://osv.dev/vulnerability/CVE-2021-3772
Type: osv

## Details
A flaw was found in the Linux SCTP stack. A blind attacker may be able to kill an existing SCTP association through invalid chunks if the attacker knows the IP-addresses and port numbers being used and the attacker can send packets with spoofed IP addresses.

## References
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://security.netapp.com/advisory/ntap-20221007-0001/
- https://www.debian.org/security/2022/dsa-5096
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2000694
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=32f8807a48ae55be0e76880cfe8607a18b5bb0df
- https://github.com/torvalds/linux/commit/32f8807a48ae55be0e76880cfe8607a18b5bb0df
- https://ubuntu.com/security/CVE-2021-3772
