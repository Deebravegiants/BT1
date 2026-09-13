# [C] CVE-2017-8359

## Summary
Severity: Critical
Advisory: CVE-2017-8359
Aliases: PYSEC-2017-101
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-30
Source: https://osv.dev/vulnerability/CVE-2017-8359
Type: osv

## Details
Google gRPC before 2017-03-29 has an out-of-bounds write caused by a heap-based use-after-free related to the grpc_call_destroy function in core/lib/surface/call.c.

## References
- http://www.securityfocus.com/bid/98280
- https://github.com/grpc/grpc/pull/10353
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=726
