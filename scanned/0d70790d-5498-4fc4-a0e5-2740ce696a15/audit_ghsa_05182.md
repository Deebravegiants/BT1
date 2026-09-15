# [M] GoClaw has a Command Injection issue

## Summary
Severity: Medium
Advisory: GHSA-6jm8-4fhr-5w64
CVE: CVE-2026-10219
CWE: CWE-77
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-6jm8-4fhr-5w64
Type: github-advisory

## Affected
- Go: `github.com/nextlevelbuilder/goclaw` — affected >=0

## Details
A vulnerability was found in nextlevelbuilder GoClaw up to 3.11.3. This impacts the function FsBridge.WriteFile of the file internal/sandbox/fsbridge.go of the component write_file Tool. Performing a manipulation results in os command injection. The attack is possible to be carried out remotely. The exploit has been made public and could be used. The pull request to fix this issue awaits acceptance.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-10219
- https://github.com/nextlevelbuilder/goclaw/issues/1121
- https://github.com/nextlevelbuilder/goclaw/pull/1155
- https://github.com/nextlevelbuilder/goclaw
- https://vuldb.com/cve/CVE-2026-10219
- https://vuldb.com/submit/821939
- https://vuldb.com/vuln/367498
- https://vuldb.com/vuln/367498/cti
