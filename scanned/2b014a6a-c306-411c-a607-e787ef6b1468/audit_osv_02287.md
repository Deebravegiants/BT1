# [H] ALPINE-CVE-2021-40330

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-40330
Ecosystem: Alpine:v3.12
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-40330
Type: osv

## Affected
- Alpine:v3.12: `git` — affected >=0 <2.26.3-r1

## Details
git_connect_git in connect.c in Git before 2.30.1 allows a repository path to contain a newline character, which may result in unexpected cross-protocol requests, as demonstrated by the git://localhost:1234/%0d%0a%0d%0aGET%20/%20HTTP/1.1 substring.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-40330
