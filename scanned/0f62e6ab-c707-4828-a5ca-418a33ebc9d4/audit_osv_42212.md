# [C] Grav before 2.0.9 Remote Code Execution via FlexDirectory

## Summary
Severity: Critical
Advisory: CVE-2026-65608
Aliases: GHSA-c4wf-2xxc-68qm
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-65608
Type: osv

## Details
Grav versions >= 1.7.0 and before 2.0.9 contain a remote code execution vulnerability. FlexDirectory::dynamicDataField() resolves blueprint data-*@: directives by calling call_user_func_array() on attacker-influenced input, validating only that the target is callable (is_callable()) without restricting dangerous functions such as exec, system, passthru, or shell_exec. Because FlexDirectory registers this handler for every Flex directory, it bypasses the validation added to Blueprint::dynamicData() in 2.0.7 (GHSA-fj2p-qj2f-74v5). Any authenticated user with create or update permission on any Flex-based directory (Flex Users, Flex Pages, Flex Objects, or custom Flex types) can execute arbitrary shell commands on the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65608.json
- https://github.com/getgrav/grav/security/advisories/GHSA-c4wf-2xxc-68qm
- https://nvd.nist.gov/vuln/detail/CVE-2026-65608
- https://www.vulncheck.com/advisories/grav-before-remote-code-execution-via-flexdirectory
- https://github.com/getgrav/grav/commit/fae9e1bf2c40ce0b50d0dfce647aaa1d22f98969
