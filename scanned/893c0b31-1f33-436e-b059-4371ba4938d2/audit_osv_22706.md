# [H] CVE-2022-36763

## Summary
Severity: High
Advisory: CVE-2022-36763
Aliases: GHSA-xvv8-66cq-prwr
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-09
Source: https://osv.dev/vulnerability/CVE-2022-36763
Type: osv

## Details
EDK2 is susceptible to a vulnerability in the Tcg2MeasureGptTable() function, allowing a user to trigger a heap buffer overflow via a local network. Successful exploitation of this vulnerability may result in a compromise of confidentiality, integrity, and/or availability.

## References
- https://lists.debian.org/debian-lts-announce/2025/06/msg00007.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SJ42V7O7F4OU6R7QSQQECLB6LDHKZIMQ/
- https://github.com/tianocore/edk2/security/advisories/GHSA-xvv8-66cq-prwr
