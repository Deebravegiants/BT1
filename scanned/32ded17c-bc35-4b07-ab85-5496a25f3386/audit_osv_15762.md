# [C] CVE-2019-19391

## Summary
Severity: Critical
Advisory: CVE-2019-19391
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-11-29
Source: https://osv.dev/vulnerability/CVE-2019-19391
Type: osv

## Details
In LuaJIT through 2.0.5, as used in Moonjit before 2.1.2 and other products, debug.getinfo has a type confusion issue that leads to arbitrary memory write or read operations, because certain cases involving valid stack levels and > options are mishandled. NOTE: The LuaJIT project owner states that the debug libary is unsafe by definition and that this is not a vulnerability. When LuaJIT was originally developed, the expectation was that the entire debug library had no security guarantees and thus it made no sense to assign CVEs. However, not all users of later LuaJIT derivatives share this perspective

## References
- https://lists.debian.org/debian-lts-announce/2025/08/msg00022.html
- https://github.com/LuaJIT/LuaJIT/pull/526
