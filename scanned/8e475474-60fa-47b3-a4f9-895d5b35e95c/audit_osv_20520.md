# [H] CVE-2021-34549

## Summary
Severity: High
Advisory: CVE-2021-34549
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-29
Source: https://osv.dev/vulnerability/CVE-2021-34549
Type: osv

## Details
An issue was discovered in Tor before 0.4.6.5, aka TROVE-2021-005. Hashing is mishandled for certain retrieval of circuit data. Consequently. an attacker can trigger the use of an attacker-chosen circuit ID to cause algorithm inefficiency.

## References
- https://blog.torproject.org/node/2041
- https://security.gentoo.org/glsa/202107-25
- https://gitlab.torproject.org/tpo/core/tor/-/issues/40391
