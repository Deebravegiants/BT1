# [H] CVE-2014-9748

## Summary
Severity: High
Advisory: CVE-2014-9748
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-11
Source: https://osv.dev/vulnerability/CVE-2014-9748
Type: osv

## Details
The uv_rwlock_t fallback implementation for Windows XP and Server 2003 in libuv before 1.7.4 does not properly prevent threads from releasing the locks of other threads, which allows attackers to cause a denial of service (deadlock) or possibly have unspecified other impact by leveraging a race condition.

## References
- https://github.com/libuv/libuv/issues/515
- https://github.com/libuv/libuv/pull/516
- https://github.com/nodejs/node/pull/2723
- https://github.com/libuv/libuv/issues/515
- https://github.com/libuv/libuv/pull/516
- https://groups.google.com/forum/#%21msg/libuv/KyNnGEXR0OA/NWb605ev2LUJ
- https://groups.google.com/forum/#%21topic/libuv/WO2cl9zasN8
