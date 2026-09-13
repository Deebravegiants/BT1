# [C] CVE-2018-1000835

## Summary
Severity: Critical
Advisory: CVE-2018-1000835
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000835
Type: osv

## Details
KeePassDX version <= 2.5.0.0beta17 contains a XML External Entity (XXE) vulnerability in kdbx file parser that can result in Disclosure of confidential data, denial of service, SSRF, port scanning.

## References
- https://0dd.zone/2018/10/28/KeePassDX-XXE/
- https://github.com/Kunzisoft/KeePassDX/issues/200
