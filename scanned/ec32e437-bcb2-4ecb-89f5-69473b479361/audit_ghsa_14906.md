# [H] LocalAI path traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-cpcx-r2gq-x893
CVE: CVE-2024-5182
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-06-20
Source: https://github.com/advisories/GHSA-cpcx-r2gq-x893
Type: github-advisory

## Affected
- Go: `github.com/go-skynet/LocalAI` — affected >=0 <2.16.0

## Details
A path traversal vulnerability exists in mudler/localai version 2.14.0, where an attacker can exploit the `model` parameter during the model deletion process to delete arbitrary files. Specifically, by crafting a request with a manipulated `model` parameter, an attacker can traverse the directory structure and target files outside of the intended directory, leading to the deletion of sensitive data. This vulnerability is due to insufficient input validation and sanitization of the `model` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5182
- https://github.com/mudler/localai/commit/1a3dedece06cab1acc3332055d285ac540a47f0e
- https://github.com/mudler/LocalAI
- https://huntr.com/bounties/f7a87f29-c22a-48e8-9fce-b6d5a273e545
