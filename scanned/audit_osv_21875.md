# [C] Memory leak in ICMP6 in Linux Kernel

## Summary
Severity: Critical
Advisory: CVE-2022-0742
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-03-18
Source: https://osv.dev/vulnerability/CVE-2022-0742
Type: osv

## Details
Memory leak in icmp6 implementation in Linux Kernel 5.13+ allows a remote attacker to DoS a host by making it go out-of-memory via icmp6 packets of type 130 or 131. We recommend upgrading past commit 2d3916f3189172d5c69d33065c3c21119fe539fc.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=2d3916f3189172d5c69d33065c3c21119fe539fc
- https://www.openwall.com/lists/oss-security/2022/03/15/3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/0xxx/CVE-2022-0742.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-0742
- https://security.netapp.com/advisory/ntap-20220425-0001/
