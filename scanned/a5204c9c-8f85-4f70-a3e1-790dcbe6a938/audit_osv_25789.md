# [H] GIMP PSP File Parsing Integer Overflow Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2023-44443
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2023-44443
Type: osv

## Details
GIMP PSP File Parsing Integer Overflow Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of GIMP. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the parsing of PSP files. The issue results from the lack of proper validation of user-supplied data, which can result in an integer overflow before writing to memory. An attacker can leverage this vulnerability to execute code in the context of the current process.
. Was ZDI-CAN-22096.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/44xxx/CVE-2023-44443.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-44443
- https://www.gimp.org/news/2023/11/07/gimp-2-10-36-released/
- https://www.zerodayinitiative.com/advisories/ZDI-23-1593/
