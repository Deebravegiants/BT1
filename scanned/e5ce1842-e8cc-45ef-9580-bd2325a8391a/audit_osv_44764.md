# [M] PX4 Autopilot through 1.17.0 Null Pointer Dereference via param select

## Summary
Severity: Medium
Advisory: CVE-2026-86097
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-86097
Type: osv

## Details
PX4 Autopilot through 1.17.0 contains a null pointer dereference vulnerability in param_set_default_file() and param_set_backup_file() functions that allows attackers to crash the autopilot process. Attackers can invoke 'param select' or 'param select-backup' commands with no path argument from any PX4 shell to trigger the crash.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86097.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86097
- https://www.vulncheck.com/advisories/px4-autopilot-through-1.17.0-null-pointer-dereference-via-param-select
- https://github.com/PX4/PX4-Autopilot/commit/02eabc08c9b8cb1de525070cacb7ea0c495136f6
- https://github.com/PX4/PX4-Autopilot/pull/28475
- https://github.com/PX4/PX4-Autopilot
- https://github.com/PX4/PX4-Autopilot/blob/v1.17.0/src/lib/parameters/parameters.cpp
