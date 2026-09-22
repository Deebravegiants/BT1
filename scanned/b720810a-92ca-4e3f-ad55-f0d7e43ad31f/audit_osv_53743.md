# [H] CVE-2023-22796

## Summary
Severity: High
Advisory: CVE-2023-22796
Aliases: GHSA-j6gc-792m-qgm2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-09
Source: https://osv.dev/vulnerability/CVE-2023-22796
Type: osv

## Details
A regular expression based DoS vulnerability in Active Support <6.1.7.1 and <7.0.4.1. A specially crafted string passed to the underscore method can cause the regular expression engine to enter a state of catastrophic backtracking. This can cause the process to use large amounts of CPU and memory, leading to a possible DoS vulnerability.

## References
- https://www.debian.org/security/2023/dsa-5372
- https://security.netapp.com/advisory/ntap-20240202-0009/
- https://discuss.rubyonrails.org/t/cve-2023-22796-possible-redos-based-dos-vulnerability-in-active-supports-underscore/82116
