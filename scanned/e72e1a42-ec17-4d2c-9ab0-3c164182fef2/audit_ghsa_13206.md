# [C] ReportLab vulnerable to remote code execution via paraparser

## Summary
Severity: Critical
Advisory: GHSA-pj98-2xf6-cff5
CVE: CVE-2019-19450
CWE: CWE-91
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-20
Source: https://github.com/advisories/GHSA-pj98-2xf6-cff5
Type: github-advisory

## Affected
- PyPI: `reportlab` — affected >=0 <3.5.31

## Details
paraparser in ReportLab before 3.5.31 allows remote code execution because start_unichar in paraparser.py evaluates untrusted user input in a unichar element in a crafted XML document with '<unichar code="' followed by arbitrary Python code, a similar issue to CVE-2019-17626.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19450
- https://github.com/MrBitBucket/reportlab-mirror/blob/master/CHANGES.md
- https://github.com/MrBitBucket/reportlab-mirror/blob/master/CHANGES.md#release-353115102019
- https://hg.reportlab.com/hg-public/reportlab
- https://lists.debian.org/debian-lts-announce/2023/09/msg00037.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CHMCB2GJQKFMGVO5RWHN222NQL5XYPHZ
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HADPTB3SBU7IVRMDK7OL6WSQRU5AFWDZ
- https://pastebin.com/5MicRrr4
