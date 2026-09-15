# [H] CVE-2018-6346

## Summary
Severity: High
Advisory: CVE-2018-6346
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-31
Source: https://osv.dev/vulnerability/CVE-2018-6346
Type: osv

## Details
A potential denial-of-service issue in the Proxygen handling of invalid HTTP2 priority settings (specifically a circular dependency). This affects Proxygen prior to v2018.12.31.00.

## References
- https://github.com/facebook/proxygen/commit/52cf331743ebd74194d6343a6c2ec52bb917c982
