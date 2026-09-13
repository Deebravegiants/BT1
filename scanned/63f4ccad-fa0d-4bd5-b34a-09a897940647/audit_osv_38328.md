# [H] CVE-2026-38969

## Summary
Severity: High
Advisory: CVE-2026-38969
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-38969
Type: osv

## Details
ruby webrick through v1.9.2 WEBrick reparses trailer Content-Length into canonical request state, enabling request smuggling. NOTE: the Supplier reports that "The project README states that it is suitable for testing and development, and that its developers do not encourage its use to serve production web applications that may be subject to hostile input. It is not a production web server and is not intended to receive traffic from untrusted sources. Request smuggling is only reachable when WEBrick sits behind a proxy and receives hostile traffic in a production deployment, which is the configuration the project documents as discouraged."

## References
- https://github.com/ruby/webrick/blob/master/README.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/38xxx/CVE-2026-38969.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-38969
- https://github.com/ruby/webrick/issues/198
- https://github.com/ruby/webrick/pull/199
