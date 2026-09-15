# [H] CVE-2017-8823

## Summary
Severity: High
Advisory: CVE-2017-8823
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-03
Source: https://osv.dev/vulnerability/CVE-2017-8823
Type: osv

## Details
In Tor before 0.2.5.16, 0.2.6 through 0.2.8 before 0.2.8.17, 0.2.9 before 0.2.9.14, 0.3.0 before 0.3.0.13, and 0.3.1 before 0.3.1.9, there is a use-after-free in onion service v2 during intro-point expiration because the expiring list is mismanaged in certain error cases, aka TROVE-2017-013.

## References
- https://blog.torproject.org/new-stable-tor-releases-security-fixes-0319-03013-02914-02817-02516
- https://bugs.torproject.org/24430
- https://www.debian.org/security/2017/dsa-4054
- https://bugs.torproject.org/24313
