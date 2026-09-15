# [M] CVE-2019-17345

## Summary
Severity: Medium
Advisory: CVE-2019-17345
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2019-10-08
Source: https://osv.dev/vulnerability/CVE-2019-17345
Type: osv

## Details
An issue was discovered in Xen 4.8.x through 4.11.x allowing x86 PV guest OS users to cause a denial of service because mishandling of failed IOMMU operations causes a bug check during the cleanup of a crashed guest.

## References
- https://seclists.org/bugtraq/2020/Jan/21
- https://www.debian.org/security/2020/dsa-4602
- https://xenbits.xen.org/xsa/advisory-291.html
- http://www.openwall.com/lists/oss-security/2019/10/25/4
- http://xenbits.xen.org/xsa/advisory-291.html
