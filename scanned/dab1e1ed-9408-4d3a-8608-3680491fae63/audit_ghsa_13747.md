# [M] AIOHTTP has problems in HTTP parser (the python one, not llhttp)

## Summary
Severity: Medium
Advisory: GHSA-gfw2-4jvh-wgfg
CVE: CVE-2023-47627
CWE: CWE-444
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-11-14
Source: https://github.com/advisories/GHSA-gfw2-4jvh-wgfg
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.8.6

## Details
# Summary
The HTTP parser in AIOHTTP has numerous problems with header parsing, which could lead to request smuggling.
This parser is only used when `AIOHTTP_NO_EXTENSIONS` is enabled (or not using a prebuilt wheel).
 
# Details

## Bug 1: Bad parsing of `Content-Length` values

### Description
RFC 9110 says this:
> `Content-Length = 1*DIGIT`

AIOHTTP does not enforce this rule, presumably because of an incorrect usage of the builtin `int` constructor. Because the `int` constructor accepts `+` and `-` prefixes, and digit-separating underscores, using `int` to parse CL values leads AIOHTTP to significant misinterpretation.

### Examples
```
GET / HTTP/1.1\r\n
Content-Length: -0\r\n
\r\n
X
```
```
GET / HTTP/1.1\r\n
Content-Length: +0_1\r\n
\r\n
X
```

### Suggested action
Verify that a `Content-Length` value consists only of ASCII digits before parsing, as the standard requires.

## Bug 2: Improper handling of NUL, CR, and LF in header values

### Description
RFC 9110 says this:
> Field values containing CR, LF, or NUL characters are invalid and dangerous, due to the varying ways that implementations might parse and interpret those characters; a recipient of CR, LF, or NUL within a field value MUST either reject the message or replace each of those characters with SP before further processing or forwarding of that message.

AIOHTTP's HTTP parser does not enforce this rule, and will happily process header values containing these three forbidden characters without replacing them with SP.
### Examples
```
GET / HTTP/1.1\r\n
Header: v\x00alue\r\n
\r\n
```
```
GET / HTTP/1.1\r\n
Header: v\ralue\r\n
\r\n
```
```
GET / HTTP/1.1\r\n
Header: v\nalue\r\n
\r\n
```
### Suggested action
Reject all messages with NUL, CR, or LF in a header value. The translation to space thing, while technically allowed, does not seem like a good idea to me.

## Bug 3: Improper stripping of whitespace before colon in HTTP headers

### Description
RFC 9112 says this:
> No whitespace is allowed between the field name and colon. In the past, differences in the handling of such whitespace have led to security vulnerabilities in request routing and response handling. A server MUST reject, with a response status code of 400 (Bad Request), any received request message that contains whitespace between a header field name and colon.

AIOHTTP does not enforce this rule, and will simply strip any whitespace before the colon in an HTTP header.

### Example
```
GET / HTTP/1.1\r\n
Content-Length : 1\r\n
\r\n
X
```

### Suggested action
Reject all messages with whitespace before a colon in a header field, as the standard requires.

# PoC
Example requests are embedded in the previous section. To reproduce these bugs, start an AIOHTTP server without llhttp (i.e. `AIOHTTP_NO_EXTENSIONS=1`) and send the requests given in the previous section. (e.g. by `printf`ing into `nc`)

# Impact
Each of these bugs can be used for request smuggling.

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-gfw2-4jvh-wgfg
- https://nvd.nist.gov/vuln/detail/CVE-2023-47627
- https://github.com/aio-libs/aiohttp/commit/d5c12ba890557a575c313bb3017910d7616fce3d
- https://github.com/aio-libs/aiohttp
- https://github.com/aio-libs/aiohttp/releases/tag/v3.8.6
- https://github.com/pypa/advisory-database/tree/main/vulns/aiohttp/PYSEC-2023-246.yaml
- https://lists.debian.org/debian-lts-announce/2025/02/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FUSJVQ7OQ55RWL4XAX2F5EZ73N4ZSH6U
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VDKQ6HM3KNDU4OQI476ZWT4O7DMSIT35
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WQYQL6WV535EEKSNH7KRARLLMOW5WXDM
