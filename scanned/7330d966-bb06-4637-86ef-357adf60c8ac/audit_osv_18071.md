# [H] CVE-2020-23490

## Summary
Severity: High
Advisory: CVE-2020-23490
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-11-16
Source: https://osv.dev/vulnerability/CVE-2020-23490
Type: osv

## Details
There was a local file disclosure vulnerability in AVideo < 8.9 via the proxy streaming. An unauthenticated attacker can exploit this issue to read an arbitrary file on the server. Which could leak database credentials or other sensitive information such as /etc/passwd file.

## References
- https://github.com/WWBN/AVideo/commit/218c98cbd4a4a2c15745852bcd0f29faf101bd8c
- https://cube01.io/blog/Avideo-Remote-Code-Execution.html
