# [H] CVE-2016-8331

## Summary
Severity: High
Advisory: CVE-2016-8331
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-10-28
Source: https://osv.dev/vulnerability/CVE-2016-8331
Type: osv

## Details
An exploitable remote code execution vulnerability exists in the handling of TIFF images in LibTIFF version 4.0.6. A crafted TIFF document can lead to a type confusion vulnerability resulting in remote code execution. This vulnerability can be triggered via a TIFF file delivered to the application using LibTIFF's tag extension functionality.

## References
- http://www.securityfocus.com/bid/93898
- https://security.gentoo.org/glsa/201701-16
- http://www.talosintelligence.com/reports/TALOS-2016-0190/
