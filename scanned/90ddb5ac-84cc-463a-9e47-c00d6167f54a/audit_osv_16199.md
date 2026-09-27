# [M] CVE-2019-3554

## Summary
Severity: Medium
Advisory: CVE-2019-3554
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-15
Source: https://osv.dev/vulnerability/CVE-2019-3554
Type: osv

## Details
Wangle's AcceptRoutingHandler incorrectly casts a socket when accepting a TLS 1.3 connection, leading to a potential denial of service attack against systems accepting such connections. This affects versions of Wangle prior to v2019.01.14.00

## References
- https://github.com/facebook/wangle/commit/3b17ba10a82c71e7808760e027ac6af687e06074
