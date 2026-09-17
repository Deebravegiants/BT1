# [C] GitPython before 3.1.59 Remote Code Execution via Config Injection

## Summary
Severity: Critical
Advisory: CVE-2026-78676
Aliases: GHSA-284h-m62q-gf8w, PYSEC-2026-3786
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-78676
Type: osv

## Details
GitPython before 3.1.59 fails to safely re-serialize multi-line git-config values during write operations, corrupting dormant quoted values into injected directives like core.hooksPath. Attackers can craft config files with embedded newlines that become live git directives after any unrelated GitPython config write, enabling arbitrary code execution via hook invocation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78676.json
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-284h-m62q-gf8w
- https://nvd.nist.gov/vuln/detail/CVE-2026-78676
- https://www.vulncheck.com/advisories/gitpython-before-remote-code-execution-via-config-injection
