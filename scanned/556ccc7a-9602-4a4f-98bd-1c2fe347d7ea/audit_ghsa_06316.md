# [M] eml_parser has parser DoS via deeply nested parentheses in e-mail headers

## Summary
Severity: Medium
Advisory: GHSA-m66c-fw79-6359
CVE: CVE-2026-55619
CWE: CWE-1124, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-m66c-fw79-6359
Type: github-advisory

## Affected
- PyPI: `eml_parser` — affected >=0 <3.0.2

## Details
### Summary

`eml_parser` uses the `email.utils.getaddresses()` function from the CPython standard library to parse e-mail headers that contain e-mail addresses (such as `To`, `Cc`, `Bcc`, `From`, `Reply-To`, `Sender`, ...). When the input header contains a deeply nested CFWS (comment / folding white space) construct, the recursive descent parser in the standard library exhausts the call stack. The resulting `RecursionError` is not caught by `eml_parser`, so the exception propagates and aborts parsing of the whole message.

### Impact

SOC pipelines use `eml_parser` to process untrusted e-mails. An attacker can easily create an eml file that will trigger the `RecursionError` during parsing.

The impact is mitigated by the fact that there are various other situations in which `eml_parser` will raise an exception when attempting to parse a malformed or pathological eml file. In particular, very deeply nested multipart e-mails also result in a `RecursionError` being raised by the library voluntarily. Therefore, systems relying on `eml_parser` already need to detect and handle errors emanating from the library in an appropriate way.

### Workarounds

The issue can be avoided by wrapping the call to `eml_parser.decode_email` or `eml_parser.decode_email_bytes` in a `try/except` construct.

### Patches

Since version 3.0.2, `eml_parser` will catch the error in the standard library parser and fall back to a simpler parser based on a regular expression.

## References
- https://github.com/GOVCERT-LU/eml_parser/security/advisories/GHSA-m66c-fw79-6359
- https://github.com/GOVCERT-LU/eml_parser/pull/90
- https://github.com/GOVCERT-LU/eml_parser/commit/746a69f86443eb0b6a47f77db3cfe727c21f92b3
- https://github.com/GOVCERT-LU/eml_parser
- https://github.com/GOVCERT-LU/eml_parser/releases/tag/v3.0.2
