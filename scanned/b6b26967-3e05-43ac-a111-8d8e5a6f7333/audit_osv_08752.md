# [H] CVE-2016-5652

## Summary
Severity: High
Advisory: CVE-2016-5652
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-01-06
Source: https://osv.dev/vulnerability/CVE-2016-5652
Type: osv

## Details
An exploitable heap-based buffer overflow exists in the handling of TIFF images in LibTIFF's TIFF2PDF tool. A crafted TIFF document can lead to a heap-based buffer overflow resulting in remote code execution. Vulnerability can be triggered via a saved TIFF file delivered by other means.

## References
- http://www.securityfocus.com/bid/93902
- http://rhn.redhat.com/errata/RHSA-2017-0225.html
- http://www.debian.org/security/2017/dsa-3762
- https://security.gentoo.org/glsa/201701-16
- http://www.talosintelligence.com/reports/TALOS-2016-0187/
