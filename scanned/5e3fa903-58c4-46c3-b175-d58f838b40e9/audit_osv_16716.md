# [H] CVE-2019-9162

## Summary
Severity: High
Advisory: CVE-2019-9162
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-25
Source: https://osv.dev/vulnerability/CVE-2019-9162
Type: osv

## Details
In the Linux kernel before 4.20.12, net/ipv4/netfilter/nf_nat_snmp_basic_main.c in the SNMP NAT module has insufficient ASN.1 length checks (aka an array index error), making out-of-bounds read and write operations possible, leading to an OOPS or local privilege escalation. This affects snmp_version and snmp_helper.

## References
- http://www.securityfocus.com/bid/107159
- https://security.netapp.com/advisory/ntap-20190327-0002/
- https://usn.ubuntu.com/3930-1/
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.19.25
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.20.12
- https://support.f5.com/csp/article/K31864522
- https://usn.ubuntu.com/3930-2/
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1776
- https://github.com/torvalds/linux/commit/c4c07b4d6fa1f11880eab8e076d3d060ef3f55fc
- https://www.exploit-db.com/exploits/46477/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c4c07b4d6fa1f11880eab8e076d3d060ef3f55fc
