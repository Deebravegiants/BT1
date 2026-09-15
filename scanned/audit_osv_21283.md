# [H] CVE-2021-41687

## Summary
Severity: High
Advisory: CVE-2021-41687
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-06-28
Source: https://osv.dev/vulnerability/CVE-2021-41687
Type: osv

## Details
DCMTK through 3.6.6 does not handle memory free properly. The program malloc a heap memory for parsing data, but does not free it when error in parsing. Sending specific requests to the dcmqrdb program incur the memory leak. An attacker can use it to launch a DoS attack.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00022.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00032.html
- https://github.com/DCMTK/dcmtk/commit/a9697dfeb672b0b9412c00c7d36d801e27ec85cb
- https://github.com/DCMTK/dcmtk
