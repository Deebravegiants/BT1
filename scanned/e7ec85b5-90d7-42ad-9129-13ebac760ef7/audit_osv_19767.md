# [M] CVE-2021-25635

## Summary
Severity: Medium
Advisory: CVE-2021-25635
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-03-21
Source: https://osv.dev/vulnerability/CVE-2021-25635
Type: osv

## Details
An Improper Certificate Validation vulnerability in LibreOffice allowed 
an attacker to self sign an ODF document, with a signature untrusted by 
the target, then modify it to change the signature algorithm to an 
invalid (or unknown to LibreOffice) algorithm and LibreOffice would incorrectly present such a signature with an unknown algorithm as a 
valid signature issued by a trusted person


This issue affects LibreOffice: from 7.0 before 7.0.5, from 7.1 before 7.1.1.

## References
- https://www.libreoffice.org/about-us/security/advisories/cve-2021-25635/
