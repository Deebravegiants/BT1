# [C] CVE-2019-20433

## Summary
Severity: Critical
Advisory: CVE-2019-20433
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-01-27
Source: https://osv.dev/vulnerability/CVE-2019-20433
Type: osv

## Details
libaspell.a in GNU Aspell before 0.60.8 has a buffer over-read for a string ending with a single '\0' byte, if the encoding is set to ucs-2 or ucs-4 outside of the application, as demonstrated by the ASPELL_CONF environment variable.

## References
- http://aspell.net/buffer-overread-ucs.txt
