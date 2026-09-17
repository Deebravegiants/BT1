# [H] CVE-2021-41689

## Summary
Severity: High
Advisory: CVE-2021-41689
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-06-28
Source: https://osv.dev/vulnerability/CVE-2021-41689
Type: osv

## Details
DCMTK through 3.6.6 does not handle string copy properly. Sending specific requests to the dcmqrdb program, it would query its database and copy the result even if the result is null, which can incur a head-based overflow. An attacker can use it to launch a DoS attack.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00022.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00032.html
- https://github.com/DCMTK/dcmtk/commit/5c14bf53fb42ceca12bbcc0016e8704b1580920d
- https://github.com/DCMTK/dcmtk
