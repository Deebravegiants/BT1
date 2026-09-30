# [H] CVE-2021-34550

## Summary
Severity: High
Advisory: CVE-2021-34550
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-29
Source: https://osv.dev/vulnerability/CVE-2021-34550
Type: osv

## Details
An issue was discovered in Tor before 0.4.6.5, aka TROVE-2021-006. The v3 onion service descriptor parsing allows out-of-bounds memory access, and a client crash, via a crafted onion service descriptor

## References
- https://blog.torproject.org/node/2041
- https://security.gentoo.org/glsa/202107-25
- https://gitlab.torproject.org/tpo/core/tor/-/issues/40392
