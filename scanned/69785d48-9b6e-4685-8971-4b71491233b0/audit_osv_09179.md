# [H] CVE-2016-8728

## Summary
Severity: High
Advisory: CVE-2016-8728
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/CVE-2016-8728
Type: osv

## Details
An exploitable heap out of bounds write vulnerability exists in the Fitz graphical library part of the MuPDF renderer. A specially crafted PDF file can cause a out of bounds write resulting in heap metadata and sensitive process memory corruption leading to potential code execution. Victim needs to open the specially crafted file in a vulnerable reader in order to trigger this vulnerability.

## References
- http://www.ghostscript.com/cgi-bin/findgit.cgi?0c86abf954ca4a5f00c26f6600acac93f9fc3538
- https://bugs.ghostscript.com/show_bug.cgi?id=697395
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2016-0242
