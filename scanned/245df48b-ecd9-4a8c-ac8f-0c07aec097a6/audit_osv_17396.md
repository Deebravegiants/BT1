# [C] CVE-2020-15007

## Summary
Severity: Critical
Advisory: CVE-2020-15007
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-24
Source: https://osv.dev/vulnerability/CVE-2020-15007
Type: osv

## Details
A buffer overflow in the M_LoadDefaults function in m_misc.c in id Tech 1 (aka Doom engine) allows arbitrary code execution via an unsafe usage of fscanf, because it does not limit the number of characters to be read in a format argument.

## References
- https://twitter.com/notrevenant/status/1268654123903340544
- https://github.com/AXDOOMER/doom-vanille/commit/8a6d9a02fa991a91ff90ccdc73b5ceabaa6cb9ec
