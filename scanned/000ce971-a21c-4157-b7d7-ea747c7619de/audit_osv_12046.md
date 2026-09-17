# [C] CVE-2018-1000837

## Summary
Severity: Critical
Advisory: CVE-2018-1000837
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000837
Type: osv

## Details
UML Designer version <= 8.0.0 contains a XML External Entity (XXE) vulnerability in XML parser for plugins that can result in Disclosure of confidential data, denial of service, SSRF, port scanning. This attack appear to be exploitable via malicious plugins.xml file.

## References
- https://github.com/ObeoNetwork/UML-Designer/issues/1035
- https://0dd.zone/2018/10/28/uml-designer-XXE/
