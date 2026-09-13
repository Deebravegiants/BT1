# [C] MOOS-IvP through 24.8.1 uMemWatch Command Injection via MOOS Client Names

## Summary
Severity: Critical
Advisory: CVE-2026-85426
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85426
Type: osv

## Details
MOOS-IvP uMemWatch through 24.8.1 constructs shell commands from attacker-chosen MOOS client names without sanitization. Attackers can inject shell metacharacters into client names to execute arbitrary commands as the uMemWatch process user through unquoted redirection targets in system calls.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85426.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85426
- https://www.vulncheck.com/advisories/moos-ivp-through-24.8.1-umemwatch-command-injection-via-moos-client-names
- https://github.com/moos-ivp/moos-ivp/commit/0b2bd991b0ca7139b1edcf271473d33e7eccfc20
- https://github.com/moos-ivp/moos-ivp/pull/121
- https://github.com/moos-ivp/moos-ivp
- https://github.com/moos-ivp/moos-ivp/blob/1de9ae146cd63c209e8c3fd81611a4ed2472971b/ivp/src/uMemWatch/MemWatch.cpp#L182
