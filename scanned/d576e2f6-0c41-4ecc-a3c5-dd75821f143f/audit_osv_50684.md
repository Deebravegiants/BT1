# [M] CVE-2020-28368

## Summary
Severity: Medium
Advisory: CVE-2020-28368
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-11-10
Source: https://osv.dev/vulnerability/CVE-2020-28368
Type: osv

## Details
Xen through 4.14.x allows guest OS administrators to obtain sensitive information (such as AES keys from outside the guest) via a side-channel attack on a power/energy monitoring interface, aka a "Platypus" attack. NOTE: there is only one logically independent fix: to change the access control for each such interface in Xen.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5J66QUUHXH2RR4CNCKQRGVXVSOUFRPDA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XV23EZIMNLJN4YXRRXLQV2ALW6ZEALXV/
- http://www.openwall.com/lists/oss-security/2020/11/26/1
- http://xenbits.xen.org/xsa/advisory-351.html
- https://platypusattack.com
- https://www.debian.org/security/2020/dsa-4804
- https://www.zdnet.com/article/new-platypus-attack-can-steal-data-from-intel-cpus/
- https://xenbits.xen.org/xsa/advisory-351.html
