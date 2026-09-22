# [H] CVE-2020-24755

## Summary
Severity: High
Advisory: CVE-2020-24755
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-05-17
Source: https://osv.dev/vulnerability/CVE-2020-24755
Type: osv

## Details
In Ubiquiti UniFi Video v3.10.13, when the executable starts, its first library validation is in the current directory. This allows the impersonation and modification of the library to execute code on the system. This was tested in (Windows 7 x64/Windows 10 x64).

## References
- https://www.youtube.com/watch?v=T41h4yeh9dk
