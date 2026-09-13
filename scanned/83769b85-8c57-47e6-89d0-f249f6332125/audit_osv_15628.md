# [M] CVE-2019-1788

## Summary
Severity: Medium
Advisory: CVE-2019-1788
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-08
Source: https://osv.dev/vulnerability/CVE-2019-1788
Type: osv

## Details
A vulnerability in the Object Linking & Embedding (OLE2) file scanning functionality of Clam AntiVirus (ClamAV) Software versions 0.101.1 and prior could allow an unauthenticated, remote attacker to cause a denial of service condition on an affected device. The vulnerability is due to a lack of proper input and validation checking mechanisms for OLE2 files sent an affected device. An attacker could exploit this vulnerability by sending malformed OLE2 files to the device running an affected version ClamAV Software. An exploit could allow the attacker to cause an out-of-bounds write condition, resulting in a crash that could result in a denial of service condition on an affected device.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00062.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00064.html
- https://lists.debian.org/debian-lts-announce/2019/04/msg00019.html
- https://security.gentoo.org/glsa/201904-12
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=12166
