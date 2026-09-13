# [H] Restricted file access on Windows in os and net/http

## Summary
Severity: High
Advisory: BIT-golang-2022-41720
Aliases: CVE-2022-41720, GO-2022-1143
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-41720
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.19.0 <1.19.4

## Details
On Windows, restricted files can be accessed via os.DirFS and http.Dir. The os.DirFS function and http.Dir type provide access to a tree of files rooted at a given directory. These functions permit access to Windows device files under that root. For example, os.DirFS("C:/tmp").Open("COM1") opens the COM1 device. Both os.DirFS and http.Dir only provide read-only filesystem access. In addition, on Windows, an os.DirFS for the directory (the root of the current drive) can permit a maliciously crafted path to escape from the drive and access any path on the system. With fix applied, the behavior of os.DirFS("") has changed. Previously, an empty root was treated equivalently to "/", so os.DirFS("").Open("tmp") would open the path "/tmp". This now returns an error.

## References
- https://go.dev/cl/455716
- https://go.dev/issue/56694
- https://groups.google.com/g/golang-announce/c/L_3rmdT0BMU/m/yZDrXjIiBQAJ
- https://pkg.go.dev/vuln/GO-2022-1143
- https://nvd.nist.gov/vuln/detail/CVE-2022-41720
