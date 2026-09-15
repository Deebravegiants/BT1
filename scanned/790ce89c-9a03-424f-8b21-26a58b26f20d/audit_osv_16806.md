# [C] CVE-2019-9827

## Summary
Severity: Critical
Advisory: CVE-2019-9827
Aliases: GHSA-mcg9-64cp-xwp7
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-03
Source: https://osv.dev/vulnerability/CVE-2019-9827
Type: osv

## Details
Hawt Hawtio through 2.5.0 is vulnerable to SSRF, allowing a remote attacker to trigger an HTTP request from an affected server to an arbitrary host via the initial /proxy/ substring of a URI.

## References
- https://www.ciphertechs.com/hawtio-advisory/
