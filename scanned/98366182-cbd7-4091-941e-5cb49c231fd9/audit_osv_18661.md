# [H] CVE-2020-3123

## Summary
Severity: High
Advisory: CVE-2020-3123
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-05
Source: https://osv.dev/vulnerability/CVE-2020-3123
Type: osv

## Details
A vulnerability in the Data-Loss-Prevention (DLP) module in Clam AntiVirus (ClamAV) Software versions 0.102.1 and 0.102.0 could allow an unauthenticated, remote attacker to cause a denial of service condition on an affected device. The vulnerability is due to an out-of-bounds read affecting users that have enabled the optional DLP feature. An attacker could exploit this vulnerability by sending a crafted email file to an affected device. An exploit could allow the attacker to cause the ClamAV scanning process crash, resulting in a denial of service condition.

## References
- https://blog.clamav.net/2020/02/clamav-01022-security-patch-released.html
- https://quickview.cloudapps.cisco.com/quickview/bug/CSCvs59062
- https://security.gentoo.org/glsa/202003-46
- https://usn.ubuntu.com/4280-1/
- https://usn.ubuntu.com/4280-2/
