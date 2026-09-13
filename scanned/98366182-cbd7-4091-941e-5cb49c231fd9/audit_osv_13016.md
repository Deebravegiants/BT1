# [M] CVE-2018-16870

## Summary
Severity: Medium
Advisory: CVE-2018-16870
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-01-03
Source: https://osv.dev/vulnerability/CVE-2018-16870
Type: osv

## Details
It was found that wolfssl before 3.15.7 is vulnerable to a new variant of the Bleichenbacher attack to perform downgrade attacks against TLS. This may lead to leakage of sensible data.

## References
- http://cat.eyalro.net/
- https://github.com/wolfSSL/wolfssl/pull/1950
