# [H] CVE-2021-38385

## Summary
Severity: High
Advisory: CVE-2021-38385
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-30
Source: https://osv.dev/vulnerability/CVE-2021-38385
Type: osv

## Details
Tor before 0.3.5.16, 0.4.5.10, and 0.4.6.7 mishandles the relationship between batch-signature verification and single-signature verification, leading to a remote assertion failure, aka TROVE-2021-007.

## References
- https://blog.torproject.org
- https://blog.torproject.org/node/2062
- https://security.gentoo.org/glsa/202305-11
- https://bugs.torproject.org/tpo/core/tor/40078
