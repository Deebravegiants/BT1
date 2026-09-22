# [H] CVE-2020-10648

## Summary
Severity: High
Advisory: CVE-2020-10648
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-03-19
Source: https://osv.dev/vulnerability/CVE-2020-10648
Type: osv

## Details
Das U-Boot through 2020.01 allows attackers to bypass verified boot restrictions and subsequently boot arbitrary images by providing a crafted FIT image to a system configured to boot the default configuration.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-577017.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00030.html
- http://www.openwall.com/lists/oss-security/2020/03/18/5
- https://github.com/u-boot/u-boot/commits/master
- https://labs.f-secure.com/advisories/das-u-boot-verified-boot-bypass/
