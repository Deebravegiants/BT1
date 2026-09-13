# [M] CVE-2018-19967

## Summary
Severity: Medium
Advisory: CVE-2018-19967
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-12-08
Source: https://osv.dev/vulnerability/CVE-2018-19967
Type: osv

## Details
An issue was discovered in Xen through 4.11.x on Intel x86 platforms allowing guest OS users to cause a denial of service (host OS hang) because Xen does not work around Intel's mishandling of certain HLE transactions associated with the KACQUIRE instruction prefix.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00057.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00072.html
- https://www.debian.org/security/2019/dsa-4369
- http://www.securityfocus.com/bid/106182
- https://support.citrix.com/article/CTX239432
- https://xenbits.xen.org/xsa/advisory-282.html
