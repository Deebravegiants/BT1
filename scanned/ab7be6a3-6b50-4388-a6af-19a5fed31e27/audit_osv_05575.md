# [H] BIT-golang-2021-3115

## Summary
Severity: High
Advisory: BIT-golang-2021-3115
Aliases: CVE-2021-3115, GO-2021-0068
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2021-3115
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.15.0 <1.15.7

## Details
Go before 1.14.14 and 1.15.x before 1.15.7 on Windows is vulnerable to Command Injection and remote code execution when using the "go get" command to fetch modules that make use of cgo (for example, cgo can execute a gcc program from an untrusted download).

## References
- https://blog.golang.org/path-security
- https://groups.google.com/g/golang-announce/c/mperVMGa98w
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YWAYJGXWC232SG3UR3TR574E6BP3OSQQ/
- https://security.gentoo.org/glsa/202208-02
- https://security.netapp.com/advisory/ntap-20210219-0001/
- https://nvd.nist.gov/vuln/detail/CVE-2021-3115
