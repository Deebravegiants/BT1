# [M] protocol-http1 HTTP Request/Response Smuggling vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6jwc-qr2q-7xwj
CVE: CVE-2023-38697
CWE: CWE-444
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2023-08-03
Source: https://github.com/advisories/GHSA-6jwc-qr2q-7xwj
Type: github-advisory

## Affected
- RubyGems: `protocol-http1` — affected >=0 <0.15.1

## Details
### Impact

[RFC 9112 Section 7.1](https://www.rfc-editor.org/rfc/rfc9112#name-chunked-transfer-coding) defined the format of chunk size, chunk data and chunk extension (detailed ABNF is in Appendix section).

In summary:

- The value of Content-Length header should be a string of 0-9 digits.
- The chunk size should be a string of hex digits and should split from chunk data using CRLF.
- The chunk extension shouldn't contain any invisible character.

However, we found that Falcon has following behaviors while disobey the corresponding RFCs.

- Falcon accepts Content-Length header values that have "+" prefix.
- Falcon accepts Content-Length header values that written in hexadecimal with "0x" prefix.
- Falcon accepts "0x" and "+" prefixed chunk size.
- Falcon accepts LF in chunk extension.

This behavior can lead to desync when forwarding through multiple HTTP parsers, potentially results in HTTP request smuggling and firewall bypassing. Note that while these issues were reproduced in Falcon (the server), the issue is with `protocol-http1` which implements the HTTP/1 protocol parser. We have not yet been advised of any real world exploit or practical attack.

### Patches

Fixed in `protocol-http1` v0.15.1+.

### Workarounds

None.

### References

https://github.com/socketry/protocol-http1/pull/20

## References
- https://github.com/socketry/protocol-http1/security/advisories/GHSA-6jwc-qr2q-7xwj
- https://nvd.nist.gov/vuln/detail/CVE-2023-38697
- https://github.com/socketry/protocol-http1/pull/20
- https://github.com/socketry/protocol-http1/commit/e11fc164fd2b36f7b7e785e69fa8859eb06bcedd
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/protocol-http1/CVE-2023-38697.yml
- https://github.com/socketry/protocol-http1
- https://www.rfc-editor.org/rfc/rfc9112#name-chunked-transfer-coding
