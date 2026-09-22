# [C] HTTP Request Smuggling: Content-Length Sent Twice in Waitress

## Summary
Severity: Critical
Advisory: GHSA-4ppp-gpcr-7qf6
CVE: CVE-2019-16792
CWE: CWE-444
Ecosystem: PyPI
Published: 2019-12-20
Source: https://github.com/advisories/GHSA-4ppp-gpcr-7qf6
Type: github-advisory

## Affected
- PyPI: `waitress` — affected >=0 <1.4.0

## Details
### Impact

Waitress would header fold a double `Content-Length` header and due to being unable to cast the now comma separated value to an integer would set the `Content-Length` to 0 internally.

So a request with:

```
Content-Length: 10
Content-Length: 10
```

would get transformed to:

```
Content-Length: 10, 10
```

Which would Waitress would then internally set to `Content-Lenght: 0`.

Waitress would then treat the request as having no body, thereby treating the body of the request as a new request in HTTP pipelining.

### Patches

This issue is fixed in Waitress 1.4.0. This brings a range of changes to harden Waitress against potential HTTP request confusions, and may change the behaviour of Waitress behind non-conformist proxies. 

The Pylons Project recommends upgrading as soon as possible, while validating that the changes in Waitress don't cause any changes in behavior.

### Workarounds

Various reverse proxies may have protections against sending potentially bad HTTP requests to the backend, and or hardening against potential issues like this. If the reverse proxy doesn't use HTTP/1.1 for connecting to the backend issues are also somewhat mitigated, as HTTP pipelining does not exist in HTTP/1.0 and Waitress will close the connection after every single request (unless the Keep Alive header is explicitly sent... so this is not a fool proof security method).

### Issues/more security issues:

* open an issue at https://github.com/Pylons/waitress/issues (if not sensitive or security related)
* email the Pylons Security mailing list: pylons-project-security@googlegroups.com (if security related)

## References
- https://github.com/Pylons/waitress/security/advisories/GHSA-4ppp-gpcr-7qf6
- https://nvd.nist.gov/vuln/detail/CVE-2019-16792
- https://github.com/Pylons/waitress/commit/575994cd42e83fd772a5f7ec98b2c56751bd3f65
- https://docs.pylonsproject.org/projects/waitress/en/latest/#security-fixes
- https://github.com/Pylons/waitress
- https://github.com/pypa/advisory-database/tree/main/vulns/waitress/PYSEC-2020-178.yaml
- https://lists.debian.org/debian-lts-announce/2022/05/msg00011.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
