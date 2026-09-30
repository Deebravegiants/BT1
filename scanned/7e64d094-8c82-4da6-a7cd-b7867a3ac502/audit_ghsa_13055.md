# [M] Tornado vulnerable to HTTP request smuggling via improper parsing of `Content-Length` fields and chunk lengths

## Summary
Severity: Medium
Advisory: GHSA-qppv-j76h-2rpx
CWE: CWE-444
Ecosystem: PyPI
Published: 2023-08-14
Source: https://github.com/advisories/GHSA-qppv-j76h-2rpx
Type: github-advisory

## Affected
- PyPI: `tornado` — affected >=0 <6.3.3

## Details
## Summary
Tornado interprets `-`, `+`, and `_` in chunk length and `Content-Length` values, which are not allowed by the HTTP RFCs. This can result in request smuggling when Tornado is deployed behind certain proxies that interpret those non-standard characters differently. This is known to apply to older versions of haproxy, although the current release is not affected.

## Details
Tornado uses the `int` constructor to parse the values of `Content-Length` headers and chunk lengths in the following locations:
### `tornado/http1connection.py:445`
```python3
            self._expected_content_remaining = int(headers["Content-Length"])
```
### `tornado/http1connection.py:621`
```python3
                content_length = int(headers["Content-Length"])  # type: Optional[int]
```
### `tornado/http1connection.py:671`
```python3
            chunk_len = int(chunk_len_str.strip(), 16)
```
Because `int("0_0") == int("+0") == int("-0") == int("0")`, using the `int` constructor to parse and validate strings that should contain only ASCII digits is not a good strategy.

## References
- https://github.com/tornadoweb/tornado/security/advisories/GHSA-qppv-j76h-2rpx
- https://github.com/tornadoweb/tornado/commit/b7a5dd29bb02950303ae96055082c12a1ea0a4fe
- https://github.com/tornadoweb/tornado
