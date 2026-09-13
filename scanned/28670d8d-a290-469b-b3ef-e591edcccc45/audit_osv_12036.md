# [C] CVE-2018-1000821

## Summary
Severity: Critical
Advisory: CVE-2018-1000821
CVSS: 10.0 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000821
Type: osv

## Details
MicroMathematics version before commit 5c05ac8 contains a XML External Entity (XXE) vulnerability in SMathStudio files that can result in Disclosure of confidential data, denial of service, SSRF, port scanning. This attack appear to be exploitable via Specially crafted SMathStudio files. This vulnerability appears to have been fixed in after commit 5c05ac8.

## References
- https://0dd.zone/2018/10/27/micromathematics-XXE/
- https://github.com/mkulesh/microMathematics/issues/79
