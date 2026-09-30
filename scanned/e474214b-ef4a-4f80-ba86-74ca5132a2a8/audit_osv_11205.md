# [M] CVE-2017-6596

## Summary
Severity: Medium
Advisory: CVE-2017-6596
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-10
Source: https://osv.dev/vulnerability/CVE-2017-6596
Type: osv

## Details
partclone.chkimg in partclone 0.2.89 is prone to a heap-based buffer overflow vulnerability due to insufficient validation of the partclone image header. An attacker may be able to launch a 'Denial of Service attack' in the context of the user running the affected application.

## References
- https://github.com/insidej/Partclone_HeapOverFlow/blob/master/README.md
