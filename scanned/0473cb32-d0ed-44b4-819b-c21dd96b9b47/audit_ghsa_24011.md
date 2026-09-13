# [M] Incorrect Default Permissions in Beego

## Summary
Severity: Medium
Advisory: GHSA-hf4p-4j9r-3cvx
CVE: CVE-2019-16355
CWE: CWE-276
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hf4p-4j9r-3cvx
Type: github-advisory

## Affected
- Go: `github.com/beego/beego` — affected >=0 <1.12.2
- Go: `github.com/astaxie/beego` — affected >=0 <1.12.2

## Details
The File Session Manager in Beego before 1.12.2 allows local users to read session files because of weak permissions for individual files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16355
- https://github.com/beego/beego/issues/3763
- https://github.com/beego/beego/pull/3975
- https://github.com/beego/beego/pull/3975/commits/f99cbe0fa40936f2f8dd28e70620c559b6e5e2fd
- https://github.com/beego/beego/commit/bac2b31afecc65d9a89f9e473b8006c5edc0c8d1
