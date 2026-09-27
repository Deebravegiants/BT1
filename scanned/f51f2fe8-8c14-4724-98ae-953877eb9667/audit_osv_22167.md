# [C] CVE-2022-23096

## Summary
Severity: Critical
Advisory: CVE-2022-23096
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-01-28
Source: https://osv.dev/vulnerability/CVE-2022-23096
Type: osv

## Details
An issue was discovered in the DNS proxy in Connman through 1.40. The TCP server reply implementation lacks a check for the presence of sufficient Header Data, leading to an out-of-bounds read.

## References
- https://git.kernel.org/pub/scm/network/connman/connman.git/log/
- https://www.openwall.com/lists/oss-security/2022/01/25/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23096.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-23096
- https://security.gentoo.org/glsa/202310-21
- https://www.debian.org/security/2022/dsa-5231
- https://lists.debian.org/debian-lts-announce/2022/02/msg00009.html
