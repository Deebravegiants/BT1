# [M] CVE-2018-18438

## Summary
Severity: Medium
Advisory: CVE-2018-18438
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-10-19
Source: https://osv.dev/vulnerability/CVE-2018-18438
Type: osv

## Details
Qemu has integer overflows because IOReadHandler and its associated functions use a signed integer data type for a size value.

## References
- http://www.openwall.com/lists/oss-security/2018/10/17/3
- http://www.securityfocus.com/bid/105953
- https://lists.gnu.org/archive/html/qemu-devel/2018-10/msg02396.html
- https://lists.gnu.org/archive/html/qemu-devel/2018-10/msg02402.html
