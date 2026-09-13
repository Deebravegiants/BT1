# [M] Beego has a file creation race condition

## Summary
Severity: Medium
Advisory: GHSA-f6px-w8rh-7r89
CVE: CVE-2019-16354
CWE: CWE-362, CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-02
Source: https://github.com/advisories/GHSA-f6px-w8rh-7r89
Type: github-advisory

## Affected
- Go: `github.com/beego/beego` — affected >=0 <1.12.2
- Go: `github.com/astaxie/beego` — affected >=0 <1.12.2

## Details
The File Session Manager in Beego 1.10.0 allows local users to read session files because there is a race condition involving file creation within a directory with weak permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16354
- https://github.com/astaxie/beego/issues/3763
- https://github.com/beego/beego/issues/3763
- https://github.com/beego/beego/pull/3975
- https://github.com/beego/beego/pull/3975/commits/f99cbe0fa40936f2f8dd28e70620c559b6e5e2fd
- https://github.com/astaxie/beego/commit/f99cbe0fa40936f2f8dd28e70620c559b6e5e2fd
- https://github.com/beego/beego/commit/bac2b31afecc65d9a89f9e473b8006c5edc0c8d1
- https://github.com/astaxie/beego
- https://github.com/astaxie/beego/blob/v1.12.2/session/sess_file.go#L142
- https://pkg.go.dev/vuln/GO-2021-0084
