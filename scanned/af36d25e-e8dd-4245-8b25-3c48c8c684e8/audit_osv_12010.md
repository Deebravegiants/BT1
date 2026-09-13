# [C] CVE-2018-1000639

## Summary
Severity: Critical
Advisory: CVE-2018-1000639
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/CVE-2018-1000639
Type: osv

## Details
LatexDraw version <=4.0 contains a XML External Entity (XXE) vulnerability in SVG parsing functionality that can result in disclosure of data, server side request forgery, port scanning, possible rce. This attack appear to be exploitable via Specially crafted SVG file.

## References
- https://github.com/arnobl/latexdraw/issues/10
- https://0dd.zone/2018/08/05/LatexDraw-XXE/
