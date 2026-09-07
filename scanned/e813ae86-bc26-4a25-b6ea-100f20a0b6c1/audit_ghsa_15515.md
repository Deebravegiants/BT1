# [C] Chaosblade vulnerable to OS command execution

## Summary
Severity: Critical
Advisory: GHSA-723h-x37g-f8qm
CVE: CVE-2023-47105
CWE: CWE-78, CWE-95
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-18
Source: https://github.com/advisories/GHSA-723h-x37g-f8qm
Type: github-advisory

## Affected
- Go: `github.com/chaosblade-io/chaosblade` — affected >=0.0.3 <1.7.4

## Details
exec.CommandContext in Chaosblade 0.3 through 1.7.3, when server mode is used, allows OS command execution via the cmd parameter without authentication.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-47105
- https://github.com/chaosblade-io/chaosblade/commit/6bc73c31e14ea2b1bfc30f359e1fe952859d9adc
- https://github.com/advisories/GHSA-723h-x37g-f8qm
- https://github.com/chaosblade-io/chaosblade
- https://github.com/chaosblade-io/chaosblade/blob/0a07380c9899febb2b544132783b376b44226cca/exec/os/executor.go#L68
- https://narrow-oatmeal-0c0.notion.site/ChaosBlade-Remote-Command-Execution-CVE-2023-47105-4f5459046488436caaec2bced6ff26d7
