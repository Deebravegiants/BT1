# [C] CVE-2017-7860

## Summary
Severity: Critical
Advisory: CVE-2017-7860
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2017-7860
Type: osv

## Details
Google gRPC before 2017-02-22 has an out-of-bounds write caused by a heap-based buffer overflow related to the parse_unix function in core/ext/client_channel/parse_address.c.

## References
- http://www.securityfocus.com/bid/97695
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=661
- https://github.com/grpc/grpc/pull/9833
