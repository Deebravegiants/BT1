# [H] Improper Restriction of XML External Entity Reference in  iText

## Summary
Severity: High
Advisory: GHSA-86p9-x5pw-94qx
CVE: CVE-2017-9096
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-86p9-x5pw-94qx
Type: github-advisory

## Affected
- Maven: `com.itextpdf:itextpdf` — affected >=0 <5.5.12
- Maven: `com.itextpdf:itextpdf` — affected >=7.0.0 <7.0.3
- Maven: `com.lowagie:itext` — affected >=0

## Details
The XML parsers in iText before 5.5.12 and 7.x before 7.0.3 do not disable external entities, which might allow remote attackers to conduct XML external entity (XXE) attacks via a crafted PDF.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9096
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03902en_us
- https://www.compass-security.com/fileadmin/Datein/Research/Advisories/CSNC-2017-017_itext_xml_external_entity_attack.txt
- https://www.oracle.com/security-alerts/cpuoct2020.html
- http://www.securityfocus.com/archive/1/541483/100/0/threaded
