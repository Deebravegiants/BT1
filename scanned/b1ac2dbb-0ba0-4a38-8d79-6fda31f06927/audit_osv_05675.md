# [H] Unexpected code execution when invoking toolchain in cmd/go

## Summary
Severity: High
Advisory: BIT-golang-2025-68119
Aliases: CVE-2025-68119, GO-2026-4338
Ecosystem: Bitnami
Published: 2026-01-31
Source: https://osv.dev/vulnerability/BIT-golang-2025-68119
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.25.0 <1.25.6

## Details
Downloading and building modules with malicious version strings can cause local code execution. On systems with Mercurial (hg) installed, downloading modules from non-standard sources (e.g., custom domains) can cause unexpected code execution due to how external VCS commands are constructed. This issue can also be triggered by providing a malicious version string to the toolchain. On systems with Git installed, downloading and building modules with malicious version strings can allow an attacker to write to arbitrary files on the filesystem. This can only be triggered by explicitly providing the malicious version strings to the toolchain and does not affect usage of @latest or bare module paths.

## References
- https://go.dev/cl/736710
- https://go.dev/issue/77099
- https://groups.google.com/g/golang-announce/c/Vd2tYVM8eUc
- https://nvd.nist.gov/vuln/detail/CVE-2025-68119
- https://pkg.go.dev/vuln/GO-2026-4338
