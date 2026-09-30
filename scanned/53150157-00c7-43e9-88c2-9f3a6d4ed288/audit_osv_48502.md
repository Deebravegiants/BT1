# [H] CVE-2017-8819

## Summary
Severity: High
Advisory: CVE-2017-8819
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-03
Source: https://osv.dev/vulnerability/CVE-2017-8819
Type: osv

## Details
In Tor before 0.2.5.16, 0.2.6 through 0.2.8 before 0.2.8.17, 0.2.9 before 0.2.9.14, 0.3.0 before 0.3.0.13, and 0.3.1 before 0.3.1.9, the replay-cache protection mechanism is ineffective for v2 onion services, aka TROVE-2017-009. An attacker can send many INTRODUCE2 cells to trigger this issue.

## References
- https://blog.torproject.org/new-stable-tor-releases-security-fixes-0319-03013-02914-02817-02516
- https://bugs.torproject.org/24244
- https://www.debian.org/security/2017/dsa-4054
