# [C] CVE-2017-5953

## Summary
Severity: Critical
Advisory: CVE-2017-5953
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-10
Source: https://osv.dev/vulnerability/CVE-2017-5953
Type: osv

## Details
vim before patch 8.0.0322 does not properly validate values for tree length when handling a spell file, which may result in an integer overflow at a memory allocation site and a resultant buffer overflow.

## References
- http://www.securityfocus.com/bid/96217
- https://groups.google.com/forum/#%21topic/vim_dev/t-3RSdEnrHY
- https://usn.ubuntu.com/4016-1/
- https://usn.ubuntu.com/4309-1/
- http://www.debian.org/security/2017/dsa-3786
- https://security.gentoo.org/glsa/201706-26
- https://github.com/vim/vim/commit/399c297aa93afe2c0a39e2a1b3f972aebba44c9d
