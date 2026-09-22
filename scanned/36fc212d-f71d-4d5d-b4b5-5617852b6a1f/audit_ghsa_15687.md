# [H] Starship vulnerable to shell injection via undocumented, unpredictable shell expansion in custom commands

## Summary
Severity: High
Advisory: GHSA-vx24-x4mv-vwr5
CVE: CVE-2024-41815
CWE: CWE-77, CWE-78
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-26
Source: https://github.com/advisories/GHSA-vx24-x4mv-vwr5
Type: github-advisory

## Affected
- crates.io: `starship` — affected >=1.0.0 <1.20.0

## Details
## Description 
Starship is a cross-shell prompt. Starting in version 1.0.0 and prior to version 1.20.0, undocumented and unpredictable shell expansion and/or quoting rules make it easily to accidentally cause shell injection when using custom commands with starship in bash. Version 1.20.0 fixes the vulnerability.

### PoC
Have some custom command which prints out information from a potentially untrusted/unverified source.
```
[custom.git_commit_name]
command = 'git show -s --format="%<(25,mtrunc)%s"'
style = "italic"
when = true
```

### Impact
This issue only affects users with custom commands, so the scope is limited, and without knowledge of others' commands, it could be hard to successfully target someone.

## References
- https://github.com/starship/starship/security/advisories/GHSA-vx24-x4mv-vwr5
- https://nvd.nist.gov/vuln/detail/CVE-2024-41815
- https://github.com/starship/starship/commit/cfc58161e0ec595db90af686ad77a73df6d44d74
- https://github.com/starship/starship
- https://github.com/starship/starship/releases/tag/v1.20.0
- https://rustsec.org/advisories/RUSTSEC-2024-0446.html
