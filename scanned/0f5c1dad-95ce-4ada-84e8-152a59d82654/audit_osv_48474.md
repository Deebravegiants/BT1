# [M] CVE-2017-7960

## Summary
Severity: Medium
Advisory: CVE-2017-7960
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-19
Source: https://osv.dev/vulnerability/CVE-2017-7960
Type: osv

## Details
The cr_input_new_from_uri function in cr-input.c in libcroco 0.6.11 and 0.6.12 allows remote attackers to cause a denial of service (heap-based buffer over-read) via a crafted CSS file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00043.html
- https://security.gentoo.org/glsa/201707-13
- https://blogs.gentoo.org/ago/2017/04/17/libcroco-heap-overflow-and-undefined-behavior/
- https://git.gnome.org/browse/libcroco/commit/?id=898e3a8c8c0314d2e6b106809a8e3e93cf9d4394
