# [M] CVE-2017-11126

## Summary
Severity: Medium
Advisory: CVE-2017-11126
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-10
Source: https://osv.dev/vulnerability/CVE-2017-11126
Type: osv

## Details
The III_i_stereo function in libmpg123/layer3.c in mpg123 through 1.25.1 allows remote attackers to cause a denial of service (buffer over-read and application crash) via a crafted audio file that is mishandled in the code for the "block_type != 2" case, a similar issue to CVE-2017-9870.

## References
- http://openwall.com/lists/oss-security/2017/07/10/4
- https://blogs.gentoo.org/ago/2017/07/03/mpg123-global-buffer-overflow-in-iii_i_stereo-layer3-c/
