# [C] CVE-2019-11940

## Summary
Severity: Critical
Advisory: CVE-2019-11940
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-04
Source: https://osv.dev/vulnerability/CVE-2019-11940
Type: osv

## Details
In the course of decompressing HPACK inside the HTTP2 protocol, an unexpected sequence of header table resize operations can place the header table into a corrupted state, leading to a use-after-free condition and undefined behavior. This issue affects Proxygen from v0.29.0 until v2017.04.03.00.

## References
- https://www.facebook.com/security/advisories/cve-2019-11940
- https://github.com/facebook/proxygen/commit/f43b134cc5c19d8532e7fb670a1c02e85f7a8d4f
