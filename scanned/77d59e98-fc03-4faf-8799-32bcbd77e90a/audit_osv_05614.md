# [C] Output of "go env" does not sanitize values in cmd/go

## Summary
Severity: Critical
Advisory: BIT-golang-2023-24531
Aliases: CVE-2023-24531, GO-2024-2962
Ecosystem: Bitnami
Published: 2024-07-04
Source: https://osv.dev/vulnerability/BIT-golang-2023-24531
Type: osv

## Affected
- Bitnami: `golang` — affected >=0 <1.21.0-0

## Details
Command go env is documented as outputting a shell script containing the Go environment. However, go env doesn't sanitize values, so executing its output as a shell script can cause various bad bahaviors, including executing arbitrary commands or inserting new environment variables. This issue is relatively minor because, in general, if an attacker can set arbitrary environment variables on a system, they have better attack vectors than making "go env" print them out.

## References
- https://go.dev/cl/488375
- https://go.dev/cl/493535
- https://go.dev/issue/58508
- https://groups.google.com/g/golang-dev/c/ixHOFpSbajE/m/8EjlbKVWAwAJ
- https://pkg.go.dev/vuln/GO-2024-2962
- https://security.netapp.com/advisory/ntap-20250328-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2023-24531
