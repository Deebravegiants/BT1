# [M] CVE-2024-56830

## Summary
Severity: Medium
Advisory: CVE-2024-56830
CVSS: 5.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-01-02
Source: https://osv.dev/vulnerability/CVE-2024-56830
Type: osv

## Details
The Net::EasyTCP package 0.15 through 0.26 for Perl uses Perl's builtin rand() if no strong randomization module is present.

## References
- https://metacpan.org/release/MNAGUIB/EasyTCP-0.26/changes
- https://lists.debian.org/debian-lts-announce/2025/04/msg00015.html
- https://github.com/briandfoy/cpan-security-advisory/issues/184
