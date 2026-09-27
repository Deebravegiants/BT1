# [C] MOOS-IvP through 24.8.1 iSay Command Injection via SAY_MOOS

## Summary
Severity: Critical
Advisory: CVE-2026-85425
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85425
Type: osv

## Details
MOOS-IvP iSay through 24.8.1 contains a remote code execution vulnerability in the SAY_MOOS variable handler that passes unsanitized text to a shell command. Attackers can publish SAY_MOOS messages containing backticks or command substitution syntax to execute arbitrary commands as the iSay process user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85425.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85425
- https://www.vulncheck.com/advisories/moos-ivp-through-24.8.1-isay-command-injection-via-say-moos
- https://github.com/moos-ivp/moos-ivp/commit/ed3a44131fd3e5528602f20adc37ba82273c1cd8
- https://github.com/moos-ivp/moos-ivp/pull/120
- https://github.com/moos-ivp/moos-ivp
- https://github.com/moos-ivp/moos-ivp/blob/1de9ae146cd63c209e8c3fd81611a4ed2472971b/ivp/src/iSay/Sayer.cpp#L416
