# [H] CVE-2016-9487

## Summary
Severity: High
Advisory: CVE-2016-9487
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-13
Source: https://osv.dev/vulnerability/CVE-2016-9487
Type: osv

## Details
EpubCheck 4.0.1 does not properly restrict resolving external entities when parsing XML in EPUB files during validation. An attacker who supplies a specially crafted EPUB file may be able to exploit this behavior to read arbitrary files, or have the victim execute arbitrary requests on his behalf, abusing the victim's trust relationship with other entities.

## References
- https://www.kb.cert.org/vuls/id/779243
- https://www.securityfocus.com/bid/94864/
