# [H] CVE-2019-12412

## Summary
Severity: High
Advisory: CVE-2019-12412
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-19
Source: https://osv.dev/vulnerability/CVE-2019-12412
Type: osv

## Details
A flaw in the libapreq2 v2.07 to v2.13 multipart parser can deference a null pointer leading to a process crash. A remote attacker could send a request causing a process crash which could lead to a denial of service attack.

## References
- https://bugs.debian.org/939937
- https://lists.apache.org/thread.html/rce5814279a615d4a17c870a3c5b77f57975874d382ffee0b73b7f9da%40%3Cmodperl.perl.apache.org%3E
