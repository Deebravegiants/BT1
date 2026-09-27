# [H] freezer,umh: Fix call_usermode_helper_exec() vs SIGKILL

## Summary
Severity: High
Advisory: CVE-2023-52704
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52704
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

freezer,umh: Fix call_usermode_helper_exec() vs SIGKILL

Tetsuo-San noted that commit f5d39b020809 ("freezer,sched: Rewrite
core freezer logic") broke call_usermodehelper_exec() for the KILLABLE
case.

Specifically it was missed that the second, unconditional,
wait_for_completion() was not optional and ensures the on-stack
completion is unused before going out-of-scope.

## References
- https://git.kernel.org/stable/c/7f9f6c54da876b3f0bece2b569456ceb96965ed7
- https://git.kernel.org/stable/c/eedeb787ebb53de5c5dcf7b7b39d01bf1b0f037d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52704.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52704
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
