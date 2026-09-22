# [M] HTTP Request Smuggling: LF vs CRLF handling in Waitress

## Summary
Severity: Medium
Advisory: GHSA-pg36-wpm5-g57p
CVE: CVE-2019-16785
CWE: CWE-444
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2019-12-20
Source: https://github.com/advisories/GHSA-pg36-wpm5-g57p
Type: github-advisory

## Affected
- PyPI: `waitress` — affected >=0 <1.4.0

## Details
### Impact

Waitress implemented a &amp;quot;MAY&amp;quot; part of the RFC7230 (https://tools.ietf.org/html/rfc7230#section-3.5) which states:

      Although the line terminator for the start-line and header fields is
      the sequence CRLF, a recipient MAY recognize a single LF as a line
      terminator and ignore any preceding CR.

Unfortunately if a front-end server does not parse header fields with an LF the same way as it does those with a CRLF it can lead to the front-end and the back-end server parsing the same HTTP message in two different ways. This can lead to a potential for HTTP request smuggling/splitting whereby Waitress may see two requests while the front-end server only sees a single HTTP message.

Example:

```
Content-Length: 100[CRLF]
X-Header: x[LF]Content-Length: 0[CRLF]
```

Would get treated by Waitress as if it were:

```
Content-Length: 100
X-Header: x
Content-Length: 0
```

This could potentially get used by attackers to split the HTTP request and smuggle a second request in the body of the first.


### Patches

This issue is fixed in Waitress 1.4.0. This brings a range of changes to harden Waitress against potential HTTP request confusions, and may change the behaviour of Waitress behind non-conformist proxies. 

Waitress no longer implements the MAY part of the specification and instead requires that all lines are terminated correctly with CRLF. If any lines are found with a bare CR or LF a 400 Bad Request is sent back to the requesting entity.

The Pylons Project recommends upgrading as soon as possible, while validating that the changes in Waitress don&amp;#39;t cause any changes in behavior.

### Workarounds

Various reverse proxies may have protections against sending potentially bad HTTP requests to the backend, and or hardening against potential issues like this. If the reverse proxy doesn&amp;#39;t use HTTP/1.1 for connecting to the backend issues are also somewhat mitigated, as HTTP pipelining does not exist in HTTP/1.0 and Waitress will close the connection after every single request (unless the Keep Alive header is explicitly sent... so this is not a fool proof security method)

### Issues/more security issues:

* open an issue at https://github.com/Pylons/waitress/issues (if not sensitive or security related)
* email the Pylons Security mailing list: pylons-project-security@googlegroups.com (if security related)

## References
- https://github.com/Pylons/waitress/security/advisories/GHSA-pg36-wpm5-g57p
- https://nvd.nist.gov/vuln/detail/CVE-2019-16785
- https://github.com/Pylons/waitress/commit/8eba394ad75deaf9e5cd15b78a3d16b12e6b0eba
- https://access.redhat.com/errata/RHSA-2020:0720
- https://docs.pylonsproject.org/projects/waitress/en/latest/#security-fixes
- https://github.com/Pylons/waitress
- https://github.com/pypa/advisory-database/tree/main/vulns/waitress/PYSEC-2019-136.yaml
- https://lists.debian.org/debian-lts-announce/2022/05/msg00011.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GVDHR2DNKCNQ7YQXISJ45NT4IQDX3LJ7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LYEOTGWJZVKPRXX2HBNVIYWCX73QYPM5
- https://www.oracle.com/security-alerts/cpuapr2022.html
