# [H] CVE-2018-12115

## Summary
Severity: High
Advisory: CVE-2018-12115
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-21
Source: https://osv.dev/vulnerability/CVE-2018-12115
Type: osv

## Details
In all versions of Node.js prior to 6.14.4, 8.11.4 and 10.9.0 when used with UCS-2 encoding (recognized by Node.js under the names `'ucs2'`, `'ucs-2'`, `'utf16le'` and `'utf-16le'`), `Buffer#write()` can be abused to write outside of the bounds of a single `Buffer`. Writes that start from the second-to-last position of a buffer cause a miscalculation of the maximum length of the input bytes to be written.

## References
- http://www.securityfocus.com/bid/105127
- https://access.redhat.com/errata/RHSA-2018:2552
- https://access.redhat.com/errata/RHSA-2018:2553
- https://access.redhat.com/errata/RHSA-2018:2944
- https://access.redhat.com/errata/RHSA-2018:2949
- https://access.redhat.com/errata/RHSA-2018:3537
- https://nodejs.org/en/blog/vulnerability/august-2018-security-releases/
- https://security.gentoo.org/glsa/202003-48
