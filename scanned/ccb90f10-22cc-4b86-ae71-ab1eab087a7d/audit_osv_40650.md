# [C] osquery: Heap buffer overflow via `authenticode` table (Windows)

## Summary
Severity: Critical
Advisory: CVE-2026-54001
Aliases: GHSA-hr28-jvpx-68cx
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-54001
Type: osv

## Details
osquery is a SQL powered operating system instrumentation, monitoring, and analytics framework. Prior to 5.23.1, on Windows, a local unprivileged attacker can cause a heap buffer out-of-bounds write if there is a query of the authenticode table targeting a maliciously crafted binary, due to publisher information parsing in getOriginalProgramName. If exploited successfully, this could allow a potential local privilege escalation from standard user to SYSTEM. This issue is fixed in version 5.23.1.

## References
- https://github.com/osquery/osquery/releases/tag/5.23.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54001.json
- https://github.com/osquery/osquery/security/advisories/GHSA-hr28-jvpx-68cx
- https://nvd.nist.gov/vuln/detail/CVE-2026-54001
- https://github.com/osquery/osquery/commit/59a808cda96d5a089cf6ec147efe152459284d54
- https://github.com/osquery/osquery/pull/8923
