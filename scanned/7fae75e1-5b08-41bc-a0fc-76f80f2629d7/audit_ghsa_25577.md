# [C] Inconsistent Interpretation of HTTP Requests in twisted.web

## Summary
Severity: Critical
Advisory: GHSA-c2jg-hw38-jrqq
CVE: CVE-2022-24801
CWE: CWE-444
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-04
Source: https://github.com/advisories/GHSA-c2jg-hw38-jrqq
Type: github-advisory

## Affected
- PyPI: `Twisted` — affected >=0 <22.4.0

## Details
The Twisted Web HTTP 1.1 server, located in the `twisted.web.http` module, parsed several HTTP request constructs more leniently than permitted by RFC 7230:

1. The Content-Length header value could have a `+` or `-` prefix.
2. Illegal characters were permitted in chunked extensions, such as the LF (`\n`) character.
3. Chunk lengths, which are expressed in hexadecimal format, could have a prefix of `0x`.
4. HTTP headers were stripped of all leading and trailing ASCII whitespace, rather than only space and HTAB (`\t`).

This non-conformant parsing can lead to desync if requests pass through multiple HTTP parsers, potentially resulting in HTTP request smuggling.

### Impact

You may be affected if:

1. You use Twisted Web's HTTP 1.1 server and/or proxy
2. You also pass requests through a different HTTP server and/or proxy

The specifics of the other HTTP parser matter. The original report notes that some versions of Apache Traffic Server and HAProxy have been vulnerable in the past. HTTP request smuggling may be a serious concern if you use a proxy to perform request validation or access control.

The Twisted Web client is not affected. The HTTP 2.0 server uses a different parser, so it is not affected.

### Patches

The issue has been addressed in Twisted 22.4.0rc1 and later.

### Workarounds

Other than upgrading Twisted, you could:

* Ensure any vulnerabilities in upstream proxies have been addressed, such as by upgrading them
* Filter malformed requests by other means, such as configuration of an upstream proxy

### Credits

This issue was initially reported by [Zhang Zeyu](https://github.com/zeyu2001).

## References
- https://github.com/twisted/twisted/security/advisories/GHSA-c2jg-hw38-jrqq
- https://nvd.nist.gov/vuln/detail/CVE-2022-24801
- https://github.com/twisted/twisted/commit/592217e951363d60e9cd99c5bbfd23d4615043ac
- https://github.com/pypa/advisory-database/tree/main/vulns/twisted/PYSEC-2022-195.yaml
- https://github.com/twisted/twisted
- https://github.com/twisted/twisted/releases/tag/twisted-22.4.0rc1
- https://lists.debian.org/debian-lts-announce/2022/05/msg00003.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7U6KYDTOLPICAVSR34G2WRYLFBD2YW5K
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GLKHA6WREIVAMBQD7KKWYHPHGGNKMAG6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7U6KYDTOLPICAVSR34G2WRYLFBD2YW5K
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GLKHA6WREIVAMBQD7KKWYHPHGGNKMAG6
- https://www.oracle.com/security-alerts/cpujul2022.html
