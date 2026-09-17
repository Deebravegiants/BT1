# [C] CVE-2018-1000221

## Summary
Severity: Critical
Advisory: CVE-2018-1000221
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/CVE-2018-1000221
Type: osv

## Details
pkgconf version 1.5.0 to 1.5.2 contains a Buffer Overflow vulnerability in dequote() that can result in dequote() function returns 1-byte allocation if initial length is 0, leading to buffer overflow. This attack appear to be exploitable via specially crafted .pc file. This vulnerability appears to have been fixed in 1.5.3.

## References
- https://git.dereferenced.org/pkgconf/pkgconf/pulls/3
