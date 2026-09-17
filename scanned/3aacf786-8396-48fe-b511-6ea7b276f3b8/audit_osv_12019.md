# [C] CVE-2018-1000652

## Summary
Severity: Critical
Advisory: CVE-2018-1000652
CVSS: 10.0 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/CVE-2018-1000652
Type: osv

## Details
JabRef version <=4.3.1 contains a XML External Entity (XXE) vulnerability in MsBibImporter XML Parser that can result in disclosure of confidential data, denial of service, server side request forgery, port scanning. This attack appear to be exploitable via Specially crafted MsBib file. This vulnerability appears to have been fixed in after commit 89f855d.

## References
- https://0dd.zone/2018/08/08/JabRef-XXE/
- https://github.com/JabRef/jabref/issues/4229
