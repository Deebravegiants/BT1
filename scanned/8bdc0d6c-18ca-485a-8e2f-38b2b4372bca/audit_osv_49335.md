# [M] CVE-2019-10207

## Summary
Severity: Medium
Advisory: CVE-2019-10207
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-25
Source: https://osv.dev/vulnerability/CVE-2019-10207
Type: osv

## Details
A flaw was found in the Linux kernel's Bluetooth implementation of UART, all versions kernel 3.x.x before 4.18.0 and kernel 5.x.x. An attacker with local access and write permissions to the Bluetooth hardware could use this flaw to issue a specially crafted ioctl function call and cause the system to crash.

## References
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10207
