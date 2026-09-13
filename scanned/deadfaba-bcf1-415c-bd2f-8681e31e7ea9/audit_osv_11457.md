# [M] CVE-2017-7890

## Summary
Severity: Medium
Advisory: CVE-2017-7890
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-08-02
Source: https://osv.dev/vulnerability/CVE-2017-7890
Type: osv

## Details
The GIF decoding function gdImageCreateFromGifCtx in gd_gif_in.c in the GD Graphics Library (aka libgd), as used in PHP before 5.6.31 and 7.x before 7.1.7, does not zero colorMap arrays before use. A specially crafted GIF image could use the uninitialized tables to read ~700 bytes from the top of the stack, potentially disclosing sensitive information.

## References
- https://www.tenable.com/security/tns-2017-12
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- http://www.debian.org/security/2017/dsa-3938
- http://www.securityfocus.com/bid/99492
- https://access.redhat.com/errata/RHSA-2018:0406
- https://access.redhat.com/errata/RHSA-2018:1296
- https://security.netapp.com/advisory/ntap-20180112-0001/
- https://bugs.php.net/bug.php?id=74435
- https://bugs.php.net/patch-display.php?bug=74435&patch=fix-74435-php-7.0&revision=1497970038
