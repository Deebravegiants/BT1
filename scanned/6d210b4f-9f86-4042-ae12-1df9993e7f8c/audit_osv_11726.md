# [C] CVE-2017-9431

## Summary
Severity: Critical
Advisory: CVE-2017-9431
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-05
Source: https://osv.dev/vulnerability/CVE-2017-9431
Type: osv

## Details
Google gRPC before 2017-04-05 has an out-of-bounds write caused by a heap-based buffer overflow related to core/lib/iomgr/error.c.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1018
- https://github.com/grpc/grpc/pull/10492
