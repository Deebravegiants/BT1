# [M] CVE-2021-47654

## Summary
Severity: Medium
Advisory: CVE-2021-47654
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47654
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

samples/landlock: Fix path_list memory leak

Clang static analysis reports this error

sandboxer.c:134:8: warning: Potential leak of memory
  pointed to by 'path_list'
        ret = 0;
              ^
path_list is allocated in parse_path() but never freed.

## References
- https://git.kernel.org/stable/c/66b513b7c64a7290c1fbb88e657f7cece992e131
- https://git.kernel.org/stable/c/017196730299ccd6eed24bbfabed8af4ffd81530
- https://git.kernel.org/stable/c/20fbf100f84b9aeb9c91421abe1927bc152bc32b
- https://git.kernel.org/stable/c/49b0d8bf05809df5f87e5c03e26d74bdfdab4571
