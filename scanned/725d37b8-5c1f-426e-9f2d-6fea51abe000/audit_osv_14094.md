# [H] CVE-2018-7167

## Summary
Severity: High
Advisory: CVE-2018-7167
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-13
Source: https://osv.dev/vulnerability/CVE-2018-7167
Type: osv

## Details
Calling Buffer.fill() or Buffer.alloc() with some parameters can lead to a hang which could result in a Denial of Service. In order to address this vulnerability, the implementations of Buffer.alloc() and Buffer.fill() were updated so that they zero fill instead of hanging in these cases. All versions of Node.js 6.x (LTS "Boron"), 8.x (LTS "Carbon"), and 9.x are vulnerable. All versions of Node.js 10.x (Current) are NOT vulnerable.

## References
- http://www.securityfocus.com/bid/106363
- https://nodejs.org/en/blog/vulnerability/june-2018-security-releases/
- https://security.gentoo.org/glsa/202003-48
