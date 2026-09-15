# [M] CVE-2017-15045

## Summary
Severity: Medium
Advisory: CVE-2017-15045
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-06
Source: https://osv.dev/vulnerability/CVE-2017-15045
Type: osv

## Details
LAME 3.99, 3.99.1, 3.99.2, 3.99.3, 3.99.4, 3.99.5, 3.98.4, 3.98.2 and 3.98 has a heap-based buffer over-read in fill_buffer in libmp3lame/util.c, related to lame_encode_buffer_sample_t in libmp3lame/lame.c, a different vulnerability than CVE-2017-9410.

## References
- https://github.com/Hack-Me/Pocs_for_Multi_Versions/tree/main/CVE-2017-15045
- https://sourceforge.net/p/lame/bugs/478/
