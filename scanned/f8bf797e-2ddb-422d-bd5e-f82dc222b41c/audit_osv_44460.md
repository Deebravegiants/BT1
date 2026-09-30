# [C] Sudo through 1.9.17p2 Intercept Policy Bypass via execveat

## Summary
Severity: Critical
Advisory: CVE-2026-82474
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-29
Source: https://osv.dev/vulnerability/CVE-2026-82474
Type: osv

## Details
Sudo through 1.9.17p2 fails to apply intercept policy checks to the execveat system call in ptrace-based intercept mode. Users permitted to run specific commands can execute denied programs by calling execveat directly or through fexecve, bypassing policy enforcement and logging.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82474.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82474
- https://www.vulncheck.com/advisories/sudo-through-1.9-17p2-intercept-policy-bypass-via-execveat
- https://github.com/sudo-project/sudo/commit/71fbe42dcd5a1c8f799540583a2dfb2ae6221edf
- https://github.com/sudo-project/sudo
- https://github.com/sudo-project/sudo/blob/v1.9.17p2/src/exec_ptrace.c
