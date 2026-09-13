# [M] CVE-2023-20569

## Summary
Severity: Medium
Advisory: CVE-2023-20569
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-08-08
Source: https://osv.dev/vulnerability/CVE-2023-20569
Type: osv

## Details
A side channel vulnerability on some of the AMD CPUs may allow an attacker to influence the return address prediction. This may result in speculative execution at an attacker-controlled address, potentially leading to information disclosure.

## References
- https://www.amd.com/en/resources/product-security/bulletin/amd-sb-7005.html
- http://xenbits.xen.org/xsa/advisory-434.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/T7WO5JM74YJSYAE5RBV4DC6A4YLEKWLF/
- https://security.netapp.com/advisory/ntap-20240605-0006/
- https://www.amd.com/en/corporate/product-security/bulletin/AMD-SB-7005
- https://www.debian.org/security/2023/dsa-5475
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HKKYIK2EASDNUV4I7EFJKNBVO3KCKGRR/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/L4E4TZNMLYL2KETY23IPA43QXFAVJ46V/
- http://www.openwall.com/lists/oss-security/2023/08/08/4
- https://lists.debian.org/debian-lts-announce/2023/08/msg00013.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PKK3IA63LSKM4EC3TN4UM6DDEIOWEQIG/
- https://comsec.ethz.ch/research/microarch/inception/
