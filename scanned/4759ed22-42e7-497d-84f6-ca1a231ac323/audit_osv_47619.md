# [H] CVE-2016-9379

## Summary
Severity: High
Advisory: CVE-2016-9379
CVSS: 7.9 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2016-9379
Type: osv

## Details
The pygrub boot loader emulator in Xen, when S-expression output format is requested, allows local pygrub-using guest OS administrators to read or delete arbitrary files on the host via string quotes and S-expressions in the bootloader configuration file.

## References
- https://security.gentoo.org/glsa/201612-56
- http://www.securityfocus.com/bid/94473
- http://www.securitytracker.com/id/1037347
- https://support.citrix.com/article/CTX218775
- http://xenbits.xen.org/xsa/advisory-198.html
- http://xenbits.xen.org/xsa/xsa198.patch
