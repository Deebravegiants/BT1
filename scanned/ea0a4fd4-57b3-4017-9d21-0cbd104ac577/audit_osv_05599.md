# [H] Empty Cmd.Path can trigger unintended binary in os/exec on Windows

## Summary
Severity: High
Advisory: BIT-golang-2022-30580
Aliases: CVE-2022-30580, GO-2022-0532
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-30580
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.18.0 <1.18.3

## Details
Code injection in Cmd.Start in os/exec before Go 1.17.11 and Go 1.18.3 allows execution of any binaries in the working directory named either "..com" or "..exe" by calling Cmd.Run, Cmd.Start, Cmd.Output, or Cmd.CombinedOutput when Cmd.Path is unset.

## References
- https://go.dev/cl/403759
- https://go.dev/issue/52574
- https://go.googlesource.com/go/+/960ffa98ce73ef2c2060c84c7ac28d37a83f345e
- https://groups.google.com/g/golang-announce/c/TzIC9-t8Ytg/m/IWz5T6x7AAAJ
- https://pkg.go.dev/vuln/GO-2022-0532
- https://nvd.nist.gov/vuln/detail/CVE-2022-30580
