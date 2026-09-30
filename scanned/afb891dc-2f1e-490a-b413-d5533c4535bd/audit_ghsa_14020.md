# [H] Flask vulnerable to possible disclosure of permanent session cookie due to missing Vary: Cookie header

## Summary
Severity: High
Advisory: GHSA-m2qf-hxjv-5gpq
CVE: CVE-2023-30861
CWE: CWE-539
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-05-01
Source: https://github.com/advisories/GHSA-m2qf-hxjv-5gpq
Type: github-advisory

## Affected
- PyPI: `Flask` — affected >=2.3.0 <2.3.2
- PyPI: `Flask` — affected >=0 <2.2.5

## Details
When all of the following conditions are met, a response containing data intended for one client may be cached and subsequently sent by a proxy to other clients. If the proxy also caches `Set-Cookie` headers, it may send one client's `session` cookie to other clients. The severity depends on the application's use of the session, and the proxy's behavior regarding cookies. The risk depends on _all_ these conditions being met.

1. The application must be hosted behind a caching proxy that does not strip cookies or ignore responses with cookies.
2. The application sets [`session.permanent = True`](https://flask.palletsprojects.com/en/2.3.x/api/#flask.session.permanent).
2. The application does not access or modify the session at any point during a request.
4. [`SESSION_REFRESH_EACH_REQUEST`](https://flask.palletsprojects.com/en/2.3.x/config/#SESSION_REFRESH_EACH_REQUEST) is enabled (the default).
5. The application does not set a `Cache-Control` header to indicate that a page is private or should not be cached.

This happens because vulnerable versions of Flask only set the `Vary: Cookie` header when the session is accessed or modified, not when it is refreshed (re-sent to update the expiration) without being accessed or modified.

## References
- https://github.com/pallets/flask/security/advisories/GHSA-m2qf-hxjv-5gpq
- https://nvd.nist.gov/vuln/detail/CVE-2023-30861
- https://github.com/pallets/flask/commit/70f906c51ce49c485f1d355703e9cc3386b1cc2b
- https://github.com/pallets/flask/commit/afd63b16170b7c047f5758eb910c416511e9c965
- https://github.com/pallets/flask
- https://github.com/pallets/flask/releases/tag/2.2.5
- https://github.com/pallets/flask/releases/tag/2.3.2
- https://github.com/pypa/advisory-database/tree/main/vulns/flask/PYSEC-2023-62.yaml
- https://lists.debian.org/debian-lts-announce/2023/08/msg00024.html
- https://security.netapp.com/advisory/ntap-20230818-0006
- https://www.debian.org/security/2023/dsa-5442
