# [H] Integer overflow in github.com/gorilla/websocket

## Summary
Severity: High
Advisory: GHSA-3xh2-74w9-5vxm
CVE: CVE-2020-27813
CWE: CWE-190, CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-3xh2-74w9-5vxm
Type: github-advisory

## Affected
- Go: `github.com/gorilla/websocket` — affected >=0 <1.4.1

## Details
An integer overflow vulnerability exists with the length of websocket frames received via a websocket connection. An attacker would use this flaw to cause a denial of service attack on an HTTP Server allowing websocket connections.

## References
- https://github.com/gorilla/websocket/security/advisories/GHSA-jf24-p9p9-4rjh
- https://nvd.nist.gov/vuln/detail/CVE-2020-27813
- https://github.com/gorilla/websocket/pull/537
- https://github.com/gorilla/websocket/commit/5b740c29263eb386f33f265561c8262522f19d37
- https://bugzilla.redhat.com/show_bug.cgi?id=1902111
- https://github.com/gorilla/websocket
- https://lists.debian.org/debian-lts-announce/2021/01/msg00008.html
- https://pkg.go.dev/vuln/GO-2020-0019
