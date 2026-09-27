# [M] CVE-2019-1787

## Summary
Severity: Medium
Advisory: CVE-2019-1787
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-08
Source: https://osv.dev/vulnerability/CVE-2019-1787
Type: osv

## Details
A vulnerability in the Portable Document Format (PDF) scanning functionality of Clam AntiVirus (ClamAV) Software versions 0.101.1 and prior could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition on an affected device. The vulnerability is due to a lack of proper data handling mechanisms within the device buffer while indexing remaining file data on an affected device. An attacker could exploit this vulnerability by sending crafted PDF files to an affected device. A successful exploit could allow the attacker to cause a heap buffer out-of-bounds read condition, resulting in a crash that could result in a denial of service condition on an affected device.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00062.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00064.html
- https://lists.debian.org/debian-lts-announce/2019/04/msg00019.html
- https://security.gentoo.org/glsa/201904-12
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=12181
