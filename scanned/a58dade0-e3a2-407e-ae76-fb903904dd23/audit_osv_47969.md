# [M] CVE-2017-15652

## Summary
Severity: Medium
Advisory: CVE-2017-15652
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2019-05-23
Source: https://osv.dev/vulnerability/CVE-2017-15652
Type: osv

## Details
Artifex Ghostscript 9.22 is affected by: Obtain Information. The impact is: obtain sensitive information. The component is: affected source code file, affected function, affected executable, affected libga (imagemagick used that). The attack vector is: Someone must open a postscript file though ghostscript. Because of imagemagick also use libga, so it was affected as well.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=2fc463d0e
- http://www.securityfocus.com/bid/108463
- https://bugs.ghostscript.com/show_bug.cgi?id=698676
