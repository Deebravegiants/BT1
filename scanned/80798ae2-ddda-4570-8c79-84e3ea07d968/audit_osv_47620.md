# [H] CVE-2016-9380

## Summary
Severity: High
Advisory: CVE-2016-9380
CVSS: 7.5 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2016-9380
Type: osv

## Details
The pygrub boot loader emulator in Xen, when nul-delimited output format is requested, allows local pygrub-using guest OS administrators to read or delete arbitrary files on the host via NUL bytes in the bootloader configuration file.

## References
- http://www.securityfocus.com/bid/94473
- http://www.securitytracker.com/id/1037347
- https://security.gentoo.org/glsa/201612-56
- http://xenbits.xen.org/xsa/advisory-198.html
- http://xenbits.xen.org/xsa/xsa198.patch
- https://support.citrix.com/article/CTX218775
