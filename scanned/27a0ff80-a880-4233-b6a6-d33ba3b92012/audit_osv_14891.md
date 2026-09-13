# [H] CVE-2019-12247

## Summary
Severity: High
Advisory: CVE-2019-12247
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-05-22
Source: https://osv.dev/vulnerability/CVE-2019-12247
Type: osv

## Details
QEMU 3.0.0 has an Integer Overflow because the qga/commands*.c files do not check the length of the argument list or the number of environment variables. NOTE: This has been disputed as not exploitable

## References
- https://lists.gnu.org/archive/html/qemu-devel/2019-05/msg05457.html
- http://www.securityfocus.com/bid/108434
- https://lists.gnu.org/archive/html/qemu-devel/2019-01/msg06360.html
- https://lists.gnu.org/archive/html/qemu-devel/2019-05/msg04596.html
