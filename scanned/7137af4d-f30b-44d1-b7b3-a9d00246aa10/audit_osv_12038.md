# [C] CVE-2018-1000825

## Summary
Severity: Critical
Advisory: CVE-2018-1000825
CVSS: 10.0 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000825
Type: osv

## Details
FreeCol version <= nightly-2018-08-22 contains a XML External Entity (XXE) vulnerability in FreeColXMLReader parser that can result in Disclosure of confidential data, denial of service, SSRF, port scanning. This attack appear to be exploitable via Freecol file.

## References
- https://0dd.zone/2018/10/28/freecol-XXE/
- https://github.com/FreeCol/freecol/issues/26
