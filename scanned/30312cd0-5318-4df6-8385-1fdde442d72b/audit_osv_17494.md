# [H] CVE-2020-15572

## Summary
Severity: High
Advisory: CVE-2020-15572
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-07-15
Source: https://osv.dev/vulnerability/CVE-2020-15572
Type: osv

## Details
Tor before 0.4.3.6 has an out-of-bounds memory access that allows a remote denial-of-service (crash) attack against Tor instances built to use Mozilla Network Security Services (NSS), aka TROVE-2020-001.

## References
- https://blog.torproject.org/new-release-tor-03511-0428-0436-security-fixes
- https://gitlab.torproject.org/tpo/core/tor/-/issues/33119
- https://trac.torproject.org/projects/tor/wiki/TROVE
