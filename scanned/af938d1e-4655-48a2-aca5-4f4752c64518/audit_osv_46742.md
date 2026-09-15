# [M] CVE-2015-0837

## Summary
Severity: Medium
Advisory: CVE-2015-0837
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-11-29
Source: https://osv.dev/vulnerability/CVE-2015-0837
Type: osv

## Details
The mpi_powm function in Libgcrypt before 1.6.3 and GnuPG before 1.4.19 allows attackers to obtain sensitive information by leveraging timing differences when accessing a pre-computed table during modular exponentiation, related to a "Last-Level Cache Side-Channel Attack."

## References
- http://www.debian.org/security/2015/dsa-3184
- http://www.debian.org/security/2015/dsa-3185
- https://ieeexplore.ieee.org/document/7163050
- https://lists.gnupg.org/pipermail/gnupg-announce/2015q1/000363.html
- https://lists.gnupg.org/pipermail/gnupg-announce/2015q1/000364.html
- https://lists.gnupg.org/pipermail/gnupg-announce/2015q1/000363.html
- https://lists.gnupg.org/pipermail/gnupg-announce/2015q1/000364.html
