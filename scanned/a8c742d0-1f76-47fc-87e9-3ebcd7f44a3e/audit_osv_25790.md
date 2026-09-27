# [H] GIMP PSP File Parsing Off-By-One Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2023-44444
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2023-44444
Type: osv

## Details
GIMP PSP File Parsing Off-By-One Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of GIMP. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the parsing of PSP files. Crafted data in a PSP file can trigger an off-by-one error when calculating a location to write within a heap-based buffer. An attacker can leverage this vulnerability to execute code in the context of the current process.
. Was ZDI-CAN-22097.

## References
- https://lists.debian.org/debian-lts-announce/2023/11/msg00015.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/44xxx/CVE-2023-44444.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-44444
- https://www.gimp.org/news/2023/11/07/gimp-2-10-36-released/
- https://www.zerodayinitiative.com/advisories/ZDI-23-1591/
