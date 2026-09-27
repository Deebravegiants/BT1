# [M] CVE-2018-12384

## Summary
Severity: Medium
Advisory: CVE-2018-12384
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-04-29
Source: https://osv.dev/vulnerability/CVE-2018-12384
Type: osv

## Details
When handling a SSLv2-compatible ClientHello request, the server doesn't generate a new random value but sends an all-zero value instead. This results in full malleability of the ClientHello for SSLv2 used for TLS 1.2 in all versions prior to NSS 3.39. This does not impact TLS 1.3.

## References
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=CVE-2018-12384
