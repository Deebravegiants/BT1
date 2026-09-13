# [H] CVE-2016-8729

## Summary
Severity: High
Advisory: CVE-2016-8729
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/CVE-2016-8729
Type: osv

## Details
An exploitable memory corruption vulnerability exists in the JBIG2 parser of Artifex MuPDF 1.9. A specially crafted PDF can cause a negative number to be passed to a memset resulting in memory corruption and potential code execution. An attacker can specially craft a PDF and send to the victim to trigger this vulnerability.

## References
- https://bugs.ghostscript.com/show_bug.cgi?id=697395
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/jbig2dec.git/commit/?id=e698d5c11d27212aa1098bc5b1673a3378563092
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/mupdf.git/commit/?id=1a7ef61410884daff8ff8391ddcecc3102acd989
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2016-0243
