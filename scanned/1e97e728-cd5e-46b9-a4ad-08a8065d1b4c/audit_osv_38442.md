# [C] UAC < 3.3.0-rc1 Command Injection via Placeholder Substitution

## Summary
Severity: Critical
Advisory: CVE-2026-40032
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-40032
Type: osv

## Details
UAC (Unix-like Artifacts Collector) before 3.3.0-rc1 contains a command injection vulnerability in the placeholder substitution and command execution pipeline where the _run_command() function passes constructed command strings directly to eval without proper sanitization. Attackers can inject shell metacharacters or command substitutions through attacker-controlled inputs including %line% values from foreach iterators and %user% / %user_home% values derived from system files to achieve arbitrary command execution with the privileges of the UAC process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40032.json
- https://mobasi.ai/sentinel
- https://nvd.nist.gov/vuln/detail/CVE-2026-40032
- https://www.vulncheck.com/advisories/uac-rc1-command-injection-via-placeholder-substitution
- https://github.com/tclahr/uac/issues/429
- https://github.com/tclahr/uac/pull/443
- https://github.com/tclahr/uac/commit/50ace60e172e38feb78347bdf579311c23eff078
- https://github.com/tclahr/uac/commit/cb95d7166cd47908e1189d9669e43f9a6d3d707f
- https://github.com/tclahr/uac/commit/d0fca5e36d8d6a33a4404f0f6fe92b0424544589
