# [C] CVE-2017-6349

## Summary
Severity: Critical
Advisory: CVE-2017-6349
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-27
Source: https://osv.dev/vulnerability/CVE-2017-6349
Type: osv

## Details
An integer overflow at a u_read_undo memory allocation site would occur for vim before patch 8.0.0377, if it does not properly validate values for tree length when reading a corrupted undo file, which may lead to resultant buffer overflows.

## References
- http://www.securityfocus.com/bid/96451
- http://www.securitytracker.com/id/1037949
- https://groups.google.com/forum/#%21topic/vim_dev/LAgsTcdSfNA
- https://groups.google.com/forum/#%21topic/vim_dev/QPZc0CY9j3Y
- https://usn.ubuntu.com/4309-1/
- https://security.gentoo.org/glsa/201706-26
- https://github.com/vim/vim/commit/3eb1637b1bba19519885dd6d377bd5596e91d22c
