# [M] Kirby: Request header injection in `Http\Remote`

## Summary
Severity: Medium
Advisory: GHSA-4v4h-m2qq-ppgw
CVE: CVE-2026-50188
CWE: CWE-113, CWE-93
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-4v4h-m2qq-ppgw
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <4.9.4
- Packagist: `getkirby/cms` — affected >=5.0.0-alpha.1 <5.4.4

## Details
### TL;DR

This vulnerability affects Kirby sites and plugins that use the `Kirby\Http\Remote` class (including `Remote::request()`, `Remote::get()`, `Remote::post()`, and similar helpers) to send outgoing HTTP requests and that pass untrusted, user-controlled data into the `headers` option of such a request.

By including newline characters in the value of the header, it was possible to inject a separate, independent header that was not intended to be set.

A successful attack requires that an application or plugin forwards attacker-influenced input into a request header value. Sites that only send static, developer-defined headers are *not* affected. The attack does not target Panel users or site visitors directly; it targets the remote service that Kirby connects to.

In Kirby's default configuration, the `Remote` class is not exposed to untrusted input, so a default installation is *not* affected. The vulnerability becomes relevant for custom code, plugins, or integrations that build request headers from user input.

----

### Introduction

HTTP header injection (also known as CRLF injection) is a type of vulnerability that allows an attacker to insert additional, attacker-controlled HTTP headers into a request or response. HTTP headers are separated by carriage-return and line-feed characters (`\r\n`). If untrusted data containing these characters is placed into a header value without sanitization, an attacker can terminate the intended header early and append headers of their own.

For outgoing requests, this means an attacker who controls part of a header value can add or override headers that the application did not intend to send. Depending on the remote service, this can be used to override security-relevant headers (such as `Authorization`, `Host`, or `Cookie`), to smuggle requests, or to poison caches on the upstream system.

Such vulnerabilities are relevant if untrusted input can reach the header values of an outgoing request – for example, a user-configurable API token, a forwarded tracking identifier, or any other value that originates from a request, form field, or content file.

### Affected components

The `Kirby\Http\Remote` class is used throughout Kirby and by plugins to perform outgoing HTTP requests. Its `headers` option allows callers to define the headers sent with the request.

As the vulnerability is in the way `Remote` assembles these headers, it affects all code paths that send a `Remote` request whose header values contain untrusted data. The Kirby core itself has not passed untrusted data in that way, but plugins or custom code might have used the class in such a way.

### Impact

In affected releases, header values passed to `Remote` were handed to the cURL request library without removing newline characters:

The `headers` option accepted arbitrary strings as header values and forwarded them to the underlying cURL request unchanged. A value containing `\r\n` was written verbatim to the socket and therefore split into several header lines on the wire.

For example, a single `X-Foo` header value of `"Bar\r\nX-Injected: pwned"` produced two separate headers in the outgoing request:

```
X-Foo: Bar
X-Injected: pwned
```

The receiving server parsed `X-Injected: pwned` as its own header. In the same way, an attacker could override a header that the application set earlier in the same request (for example, replacing a legitimate `Authorization` header).

The vulnerability allows attackers to inject or override HTTP headers in outgoing requests, provided the affected application or plugin includes attacker-controlled data in a header value.

### Patches

The problem has been patched in [Kirby 4.9.4](https://github.com/getkirby/kirby/releases/tag/4.9.4) and [Kirby 5.4.4](https://github.com/getkirby/kirby/releases/tag/5.4.4). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, we now strip carriage-return and line-feed characters from header values before they are passed to the underlying request, preventing additional headers from being injected.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-4v4h-m2qq-ppgw
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/4.9.4
- https://github.com/getkirby/kirby/releases/tag/5.4.4
