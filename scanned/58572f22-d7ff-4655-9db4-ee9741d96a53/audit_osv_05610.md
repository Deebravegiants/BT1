# [H] Unsanitized NUL in environment variables on Windows in syscall and os/exec

## Summary
Severity: High
Advisory: BIT-golang-2022-41716
Aliases: CVE-2022-41716, GO-2022-1095
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-41716
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.19.0 <1.19.3

## Details
Due to unsanitized NUL values, attackers may be able to maliciously set environment variables on Windows. In syscall.StartProcess and os/exec.Cmd, invalid environment variable values containing NUL values are not properly checked for. A malicious environment variable value can exploit this behavior to set a value for a different environment variable. For example, the environment variable string "A=B\x00C=D" sets the variables "A=B" and "C=D".

## References
- https://go.dev/cl/446916
- https://go.dev/issue/56284
- https://groups.google.com/g/golang-announce/c/mbHY1UY3BaM/m/hSpmRzk-AgAJ
- https://pkg.go.dev/vuln/GO-2022-1095
- https://security.netapp.com/advisory/ntap-20230120-0007/
- https://nvd.nist.gov/vuln/detail/CVE-2022-41716
