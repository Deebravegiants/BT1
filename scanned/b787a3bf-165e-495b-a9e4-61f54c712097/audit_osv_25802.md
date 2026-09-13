# [H] OpenPrinting CUPS/libppd Postscript Parsing Heap Overflow

## Summary
Severity: High
Advisory: CVE-2023-4504
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-09-21
Source: https://osv.dev/vulnerability/CVE-2023-4504
Type: osv

## Details
Due to failure in validating the length provided by an attacker-crafted PPD PostScript document, CUPS and libppd are susceptible to a heap-based buffer overflow and possibly code execution. This issue has been fixed in CUPS version 2.4.7, released in September of 2023.

## References
- http://seclists.org/fulldisclosure/2024/Sep/33
- https://lists.debian.org/debian-lts-announce/2023/09/msg00041.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5WHEJIYMMAIXU2EC35MGTB5LGGO2FFJE/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5WVS4I7JG3LISFPKTM6ADKJXXEPEEWBQ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AMYDKIE4PSJDEMC5OWNFCDMHFGLJ57XG/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PXPVADB56NMLJWG4IZ3OZBNJ2ZOLPQJ6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/T2GSPQAFK2Z6L57TRXEKZDF42K2EVBH7/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4504.json
- https://github.com/OpenPrinting/cups/releases/tag/v2.4.7
- https://github.com/OpenPrinting/cups/security/advisories/GHSA-pf5r-86w9-678h
- https://github.com/OpenPrinting/libppd/security/advisories/GHSA-4f65-6ph5-qwh6
- https://nvd.nist.gov/vuln/detail/CVE-2023-4504
- https://takeonme.org/cves/CVE-2023-4504.html
