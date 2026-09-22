# [H] Link Following in Iris

## Summary
Severity: High
Advisory: GHSA-jcxc-rh6w-wf49
CVE: CVE-2021-23772
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-jcxc-rh6w-wf49
Type: github-advisory

## Affected
- Go: `github.com/kataras/iris/v12` — affected >=0 <12.2.0-alpha8
- Go: `github.com/kataras/iris` — affected >=0

## Details
This affects all versions of package github.com/kataras/iris; all versions of package github.com/kataras/iris/v12. The unsafe handling of file names during upload using UploadFormFiles method may enable attackers to write to arbitrary locations outside the designated target folder.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23772
- https://github.com/kataras/iris/commit/e213dba0d32ff66653e0ef124bc5088817264b08
- https://github.com/kataras/iris
- https://pkg.go.dev/vuln/GO-2022-0272
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMKATARASIRIS-2325169
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMKATARASIRISV12-2325170
