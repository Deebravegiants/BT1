# [C] openc3-api Vulnerable to Unauthenticated Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-w757-4qv9-mghp
CVE: CVE-2025-68271
CWE: CWE-95
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-w757-4qv9-mghp
Type: github-advisory

## Affected
- RubyGems: `openc3` — affected >=5.0.6 <6.10.2

## Details
### Summary
OpenC3 COSMOS contains a critical remote code execution vulnerability reachable through the JSON-RPC API. When a JSON-RPC request uses the string form of certain APIs, attacker-controlled parameter text is parsed into values using String#convert_to_value. For array-like inputs, convert_to_value executes eval().

Because the cmd code path parses the command string before calling authorize(), an unauthenticated attacker can trigger Ruby code execution even though the request ultimately fails authorization (401).

## References
- https://github.com/OpenC3/cosmos/security/advisories/GHSA-w757-4qv9-mghp
- https://nvd.nist.gov/vuln/detail/CVE-2025-68271
- https://github.com/OpenC3/cosmos/commit/01e9fbc5e66e9a2500b71a75a44775dd1fc2d1de
- https://github.com/OpenC3/cosmos
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/openc3/CVE-2025-68271.yml
