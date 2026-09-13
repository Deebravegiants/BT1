# [M] HTTP Request Smuggling: Invalid Transfer-Encoding in Waitress

## Summary
Severity: Medium
Advisory: GHSA-g2xc-35jw-c63p
CVE: CVE-2019-16786
CWE: CWE-444
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2019-12-20
Source: https://github.com/advisories/GHSA-g2xc-35jw-c63p
Type: github-advisory

## Affected
- PyPI: `waitress` — affected >=0 <1.4.0

## Details
### Impact

Waitress would parse the `Transfer-Encoding` header and only look for a single string value, if that value was not `chunked` it would fall through and use the `Content-Length` header instead.

According to the HTTP standard `Transfer-Encoding` should be a comma separated list, with the inner-most encoding first, followed by any further transfer codings, ending with `chunked`.

Requests sent with:

```
Transfer-Encoding: gzip, chunked
```

Would incorrectly get ignored, and the request would use a `Content-Length` header instead to determine the body size of the HTTP message.

This could allow for Waitress to treat a single request as multiple requests in the case of HTTP pipelining.

### Patches

This issue is fixed in Waitress 1.4.0. This brings a range of changes to harden Waitress against potential HTTP request confusions, and may change the behaviour of Waitress behind non-conformist proxies. 

Waitress will now return a 501 Not Implemented error if the `Transfer-Encoding` is not `chunked` or contains multiple elements. Waitress does not support any transfer codings such as `gzip` or `deflate`.

The Pylons Project recommends upgrading as soon as possible, while validating that the changes in Waitress don&#39;t cause any changes in behavior.

### Workarounds

Various reverse proxies may have protections against sending potentially bad HTTP requests to the backend, and or hardening against potential issues like this. If the reverse proxy doesn&#39;t use HTTP/1.1 for connecting to the backend issues are also somewhat mitigated, as HTTP pipelining does not exist in HTTP/1.0 and Waitress will close the connection after every single request (unless the Keep Alive header is explicitly sent... so this is not a fool proof security method).

### Issues/more security issues:

* open an issue at https://github.com/Pylons/waitress/issues (if not sensitive or security related)
* email the Pylons Security mailing list: pylons-project-security@googlegroups.com (if security related)

## References
- https://github.com/Pylons/waitress/security/advisories/GHSA-g2xc-35jw-c63p
- https://nvd.nist.gov/vuln/detail/CVE-2019-16786
- https://github.com/Pylons/waitress/commit/f11093a6b3240fc26830b6111e826128af7771c3
- https://access.redhat.com/errata/RHSA-2020:0720
- https://docs.pylonsproject.org/projects/waitress/en/latest/#security-fixes
- https://github.com/Pylons/waitress
- https://github.com/pypa/advisory-database/tree/main/vulns/waitress/PYSEC-2019-137.yaml
- https://lists.debian.org/debian-lts-announce/2022/05/msg00011.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GVDHR2DNKCNQ7YQXISJ45NT4IQDX3LJ7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LYEOTGWJZVKPRXX2HBNVIYWCX73QYPM5
- https://www.oracle.com/security-alerts/cpuapr2022.html
