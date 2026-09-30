# [H] Beego privilege escalation vulnerability

## Summary
Severity: High
Advisory: GHSA-wr3p-r5fj-wf97
CVE: CVE-2024-40465
CWE: CWE-327, CWE-328
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-31
Source: https://github.com/advisories/GHSA-wr3p-r5fj-wf97
Type: github-advisory

## Affected
- Go: `github.com/beego/beego/v2` — affected >=0 <2.2.1

## Details
An issue in beego v.2.2.0 and before allows a remote attacker to escalate privileges via the `getCacheFileName` function in the `file.go` file.

## References
- https://github.com/beego/beego/security/advisories/GHSA-6g9p-wv47-4fxq
- https://nvd.nist.gov/vuln/detail/CVE-2024-40465
- https://github.com/beego/beego/commit/5a366cd62b555354a917a2d153e6563fe4d6eb88
- https://github.com/beego/beego/commit/8f89e12e6cafb106d5c201dbc3b2a338bfde74e2
- https://gist.github.com/nyxfqq/a5a2fc5147a1b34538e1ac05a3e56910
- https://github.com/beego/beego
