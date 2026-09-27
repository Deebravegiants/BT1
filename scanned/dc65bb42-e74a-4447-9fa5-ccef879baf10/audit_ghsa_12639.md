# [C] Brook's tproxy server is vulnerable to a drive-by command injection.

## Summary
Severity: Critical
Advisory: GHSA-vfrj-fv6p-3cpf
CVE: CVE-2023-33965
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-06
Source: https://github.com/advisories/GHSA-vfrj-fv6p-3cpf
Type: github-advisory

## Affected
- Go: `github.com/txthinking/brook` — affected >=0 <20230606

## Details
The `tproxy` server is vulnerable to a drive-by command injection. An attacker may fool a victim into visiting a malicious web page which will trigger requests to the local `tproxy` service leading to remote code execution.

## References
- https://github.com/txthinking/brook/security/advisories/GHSA-vfrj-fv6p-3cpf
- https://nvd.nist.gov/vuln/detail/CVE-2023-33965
- https://github.com/txthinking/brook/commit/314d7070c37babf6c38a0fe1eada872bb74bf03e
- https://github.com/txthinking/brook
