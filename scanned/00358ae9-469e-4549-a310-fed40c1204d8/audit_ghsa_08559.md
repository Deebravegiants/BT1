# [M] eml_parser has recursion DoS via nested message/rfc822 attachments

## Summary
Severity: Medium
Advisory: GHSA-g47v-rwmh-r9f8
CVE: CVE-2026-44844
CWE: CWE-674
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-g47v-rwmh-r9f8
Type: github-advisory

## Affected
- PyPI: `eml_parser` — affected >=0 <3.0.1

## Details
### Summary

`EmlParser.get_raw_body_text()` recurses unconditionally for every nested `message/rfc822` attachment without any depth limit. An attacker who can supply a badly crafted EML file with approximately 120 nested `message/rfc822` parts triggers an unhandled `RecursionError` and aborts parsing of the message. A 12 KB EML file is enough to crash a worker.
Though this causes the parser to crash, it is an unlikely scenario as the suggested EML that crashes the parser would not pass basic RFC compliance tests.

### Details

The vulnerable function is `EmlParser.get_raw_body_text()` in `eml_parser/parser.py`. For every part of type `multipart/*`, the function iterates over its sub-parts; for every sub-part of type `message/rfc822`, it calls itself recursively on the inner message:

There is no depth parameter and no early-abort. CPython's default `sys.recursionlimit` is 1000. Each level of `message/rfc822` nesting adds approximately 8 frames to the stack (parser code + stdlib `_header_value_parser` calls), so roughly 120 nested levels exhaust the limit.

The `RecursionError` is not caught anywhere along the call chain, so it propagates out of `decode_email_bytes()` and aborts processing of the entire message.


### PoC

Environment: Python 3.12.3, eml_parser 3.0.0 (`pip install eml_parser==3.0.0`), default `sys.recursionlimit=1000`, Ubuntu 24.04 aarch64. No special configuration of `EmlParser`, default constructor.

Self-contained reproducer that builds the PoC and triggers the crash:

```python
import eml_parser

def build_poc(depth=124):
    inner = b"From: a@a\r\nTo: b@b\r\nContent-Type: text/plain\r\n\r\n.\r\n"
    msg = inner
    for i in range(depth):
        b = f"B{i}".encode()
        msg = (
            b'Content-Type: multipart/mixed; boundary="' + b + b'"\r\n\r\n'
            b'--' + b + b'\r\nContent-Type: message/rfc822\r\n\r\n'
        ) + msg + b'\r\n--' + b + b'--\r\n'
    return msg

ep = eml_parser.EmlParser()
ep.decode_email_bytes(build_poc())
# RecursionError after ~76 ms on Apple Silicon (Ubuntu 24.04 aarch64).
```

Note that the suggested code does not produce an RFC compliant message.
Resulting EML payload size: 12,369 bytes.
SHA-256 of generated PoC: `00f15f635e21b4144967c2893b37425e6a6bd7b4185c557e5c7e904e1e6d18e8`

The crash is deterministic on a stock install. No network, no special headers, no large attachments.

### Impact

Denial of service of any pipeline that processes attacker-supplied EML files using `eml_parser`.

A single 12 KB email is enough to crash a worker. If the worker is a long-running process triaging multiple emails, the unhandled exception aborts processing of the whole batch unless the caller wraps the call in a broad `try/except`. Even then, attacker-supplied volume can keep workers in a perpetual restart loop.

The vulnerability is exploitable pre-authentication in any deployment that ingests emails from external senders which have not been subject to any kind of basic validation.
Considering that email messages pass through a mail-server which does some kind of validation, messages as produced by the  *build_poc* function would not reach eml_parser.
Nonetheless recursion depth checks have been implemented to handle the described issue.


### Reporter

Sebastián Alba Vives (`@Sebasteuo`)
Independent security researcher, Senior AppSec Consultant
LinkedIn: https://www.linkedin.com/in/sebastian-alba
Email: sebasjosue84@gmail.com
PGP: `0D1A E4C2 CFC8 894F 19EA  DA24 45CD CA33 2CF8 31F4`

## References
- https://github.com/GOVCERT-LU/eml_parser/security/advisories/GHSA-g47v-rwmh-r9f8
- https://nvd.nist.gov/vuln/detail/CVE-2026-44844
- https://github.com/GOVCERT-LU/eml_parser
