# [C] Apache bRPC: Remote command injection vulnerability in heap builtin service

## Summary
Severity: Critical
Advisory: CVE-2025-60021
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-16
Source: https://osv.dev/vulnerability/CVE-2025-60021
Type: osv

## Details
Remote command injection vulnerability in heap profiler builtin service in Apache bRPC ((all versions < 1.15.0)) on all platforms allows attacker to inject remote command.



Root Cause: The bRPC heap profiler built-in service (/pprof/heap) does not validate the user-provided extra_options parameter and executes it as a command-line argument. Attackers can execute remote commands using the extra_options parameter..

Affected scenarios: Use the built-in bRPC heap profiler service to perform jemalloc memory profiling.

How to Fix: we provide two methods, you can choose one of them:

1. Upgrade bRPC to version 1.15.0.
2. Apply this patch ( https://github.com/apache/brpc/pull/3101 ) manually.

## References
- http://www.openwall.com/lists/oss-security/2026/01/16/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60021.json
- https://lists.apache.org/thread/xy51d2fx6drzhfp92xptsx5845q7b37m
- https://nvd.nist.gov/vuln/detail/CVE-2025-60021
