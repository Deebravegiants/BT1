# [H] Unsafe behavior in setuid/setgid binaries in runtime

## Summary
Severity: High
Advisory: BIT-golang-2023-29403
Aliases: CVE-2023-29403, GO-2023-1840
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2023-29403
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.20.0 <1.20.5

## Details
On Unix platforms, the Go runtime does not behave differently when a binary is run with the setuid/setgid bits. This can be dangerous in certain cases, such as when dumping memory state, or assuming the status of standard i/o file descriptors. If a setuid/setgid binary is executed with standard I/O file descriptors closed, opening any files can result in unexpected content being read or written with elevated privileges. Similarly, if a setuid/setgid program is terminated, either via panic or signal, it may leak the contents of its registers.

## References
- https://go.dev/cl/501223
- https://go.dev/issue/60272
- https://groups.google.com/g/golang-announce/c/q5135a9d924/m/j0ZoAJOHAwAJ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NZ2O6YCO2IZMZJELQGZYR2WAUNEDLYV6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XBS3IIK6ADV24C5ULQU55QLT2UE762ZX/
- https://pkg.go.dev/vuln/GO-2023-1840
- https://security.gentoo.org/glsa/202311-09
- https://security.netapp.com/advisory/ntap-20241220-0009/
- https://nvd.nist.gov/vuln/detail/CVE-2023-29403
