# [H] CVE-2018-6347

## Summary
Severity: High
Advisory: CVE-2018-6347
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-31
Source: https://osv.dev/vulnerability/CVE-2018-6347
Type: osv

## Details
An issue in the Proxygen handling of HTTP2 parsing of headers/trailers can lead to a denial-of-service attack. This affects Proxygen prior to v2018.12.31.00.

## References
- https://github.com/facebook/proxygen/commit/223e0aa6bc7590e86af1e917185a2e0efe160711
