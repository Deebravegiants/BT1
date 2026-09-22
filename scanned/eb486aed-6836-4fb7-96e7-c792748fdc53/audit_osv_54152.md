# [H] CVE-2023-40477

## Summary
Severity: High
Advisory: CVE-2023-40477
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2023-40477
Type: osv

## Details
RARLAB WinRAR Recovery Volume Improper Validation of Array Index Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of RARLAB WinRAR. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the processing of recovery volumes. The issue results from the lack of proper validation of user-supplied data, which can result in a memory access past the end of an allocated buffer. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-21233.

## References
- https://lists.debian.org/debian-lts-announce/2023/11/msg00009.html
- https://www.win-rar.com/singlenewsview.html?&L=0&tx_ttnews%5Btt_news%5D=232&cHash=c5bf79590657e32554c6683296a8e8aa
- https://www.zerodayinitiative.com/advisories/ZDI-23-1152/
