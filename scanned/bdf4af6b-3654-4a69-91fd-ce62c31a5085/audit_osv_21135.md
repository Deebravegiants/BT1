# [H] CVE-2021-40848

## Summary
Severity: High
Advisory: CVE-2021-40848
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-11-03
Source: https://osv.dev/vulnerability/CVE-2021-40848
Type: osv

## Details
In Mahara before 20.04.5, 20.10.3, 21.04.2, and 21.10.0, exported CSV files could contain characters that a spreadsheet program could interpret as a command, leading to execution of a malicious string locally on a device, aka CSV injection.

## References
- https://bugs.launchpad.net/mahara/+bug/1930471
- https://mahara.org/interaction/forum/topic.php?id=8950
