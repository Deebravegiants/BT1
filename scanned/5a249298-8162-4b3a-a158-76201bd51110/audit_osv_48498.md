# [H] CVE-2017-8419

## Summary
Severity: High
Advisory: CVE-2017-8419
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-05-02
Source: https://osv.dev/vulnerability/CVE-2017-8419
Type: osv

## Details
LAME through 3.99.5 relies on the signed integer data type for values in a WAV or AIFF header, which allows remote attackers to cause a denial of service (stack-based buffer overflow or heap-based buffer overflow) or possibly have unspecified other impact via a crafted file, as demonstrated by mishandling of num_channels.

## References
- https://sourceforge.net/p/lame/bugs/458/
