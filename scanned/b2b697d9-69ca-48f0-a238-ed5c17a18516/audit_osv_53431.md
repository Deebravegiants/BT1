# [H] CVE-2022-42330

## Summary
Severity: High
Advisory: CVE-2022-42330
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-26
Source: https://osv.dev/vulnerability/CVE-2022-42330
Type: osv

## Details
Guests can cause Xenstore crash via soft reset When a guest issues a "Soft Reset" (e.g. for performing a kexec) the libxl based Xen toolstack will normally perform a XS_RELEASE Xenstore operation. Due to a bug in xenstored this can result in a crash of xenstored. Any other use of XS_RELEASE will have the same impact.

## References
- https://xenbits.xenproject.org/xsa/advisory-425.txt
- http://xenbits.xen.org/xsa/advisory-425.html
- https://security.gentoo.org/glsa/202402-07
