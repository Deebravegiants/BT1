# [H] CVE-2018-1000548

## Summary
Severity: High
Advisory: CVE-2018-1000548
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-06-26
Source: https://osv.dev/vulnerability/CVE-2018-1000548
Type: osv

## Details
Umlet version < 14.3 contains a XML External Entity (XXE) vulnerability in File parsing that can result in disclosure of confidential data, denial of service, server side request forgery. This attack appear to be exploitable via Specially crafted UXF file. This vulnerability appears to have been fixed in 14.3.

## References
- http://0dd.zone/2018/04/23/UMLet-XXE/
- https://github.com/umlet/umlet/issues/500
