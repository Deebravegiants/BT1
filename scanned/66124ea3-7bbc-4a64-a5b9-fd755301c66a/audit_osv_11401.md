# [H] CVE-2017-7619

## Summary
Severity: High
Advisory: CVE-2017-7619
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-10
Source: https://osv.dev/vulnerability/CVE-2017-7619
Type: osv

## Details
In ImageMagick 7.0.4-9, an infinite loop can occur because of a floating-point rounding error in some of the color algorithms. This affects ModulateHSL, ModulateHCL, ModulateHCLp, ModulateHSB, ModulateHSI, ModulateHSV, ModulateHWB, ModulateLCHab, and ModulateLCHuv.

## References
- http://www.securityfocus.com/bid/98689
- http://www.debian.org/security/2017/dsa-3863
- https://www.imagemagick.org/discourse-server/viewtopic.php?f=3&t=31506
