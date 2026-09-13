# [H] CVE-2021-34430

## Summary
Severity: High
Advisory: CVE-2021-34430
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-07-08
Source: https://osv.dev/vulnerability/CVE-2021-34430
Type: osv

## Details
Eclipse TinyDTLS through 0.9-rc1 relies on the rand function in the C library, which makes it easier for remote attackers to compute the master key and then decrypt DTLS traffic.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=568803
