# [C] CVE-2017-6350

## Summary
Severity: Critical
Advisory: CVE-2017-6350
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-27
Source: https://osv.dev/vulnerability/CVE-2017-6350
Type: osv

## Details
An integer overflow at an unserialize_uep memory allocation site would occur for vim before patch 8.0.0378, if it does not properly validate values for tree length when reading a corrupted undo file, which may lead to resultant buffer overflows.

## References
- http://www.securityfocus.com/bid/96448
- http://www.securitytracker.com/id/1037949
- https://groups.google.com/forum/#%21topic/vim_dev/L_dOHOOiQ5Q
- https://groups.google.com/forum/#%21topic/vim_dev/QPZc0CY9j3Y
- https://usn.ubuntu.com/4309-1/
- https://security.gentoo.org/glsa/201706-26
- https://github.com/vim/vim/commit/0c8485f0e4931463c0f7986e1ea84a7d79f10c75
