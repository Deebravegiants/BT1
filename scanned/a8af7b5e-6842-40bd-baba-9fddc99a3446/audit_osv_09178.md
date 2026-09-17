# [H] CVE-2016-8707

## Summary
Severity: High
Advisory: CVE-2016-8707
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-12-23
Source: https://osv.dev/vulnerability/CVE-2016-8707
Type: osv

## Details
An exploitable out of bounds write exists in the handling of compressed TIFF images in ImageMagicks's convert utility. A crafted TIFF document can lead to an out of bounds write which in particular circumstances could be leveraged into remote code execution. The vulnerability can be triggered through any user controlled TIFF that is handled by this functionality.

## References
- http://www.debian.org/security/2017/dsa-3799
- http://www.securityfocus.com/bid/94727
- http://www.talosintelligence.com/reports/TALOS-2016-0216/
