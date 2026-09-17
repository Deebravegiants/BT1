# [H] CVE-2023-39915

## Summary
Severity: High
Advisory: CVE-2023-39915
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-13
Source: https://osv.dev/vulnerability/CVE-2023-39915
Type: osv

## Details
NLnet Labs' Routinator up to and including version 0.12.1 may crash when trying to parse certain malformed RPKI objects. This is due to insufficient input checking in the bcder library covered by CVE-2023-39914.

## References
- https://nlnetlabs.nl/downloads/routinator/CVE-2023-39915.txt
