# [H] Litestar allows unbounded resource consumption (DoS vulnerability) 

## Summary
Severity: High
Advisory: GHSA-gjcc-jvgw-wvwj
CVE: CVE-2024-52581
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-11-20
Source: https://github.com/advisories/GHSA-gjcc-jvgw-wvwj
Type: github-advisory

## Affected
- PyPI: `litestar` — affected >=0 <2.13.0
- PyPI: `starlite` — affected >=0

## Details
### Summary
Litestar offers multiple methods to return a parsed representation of the request body, as well as extractors that rely on those parsers to map request content to structured data types. Multiple of those parsers do not have size limits when reading the request body into memory, which allows an attacker to cause excessive memory consumption on the server by sending large requests.

### Details
The `Request` methods to parse json, msgpack or form-data all read the entire request stream into memory via `await self.body()` without a prior size check or size limit. There may be other places (e.g. extractors) where this can happen.

For most formats, a configurable size limit would be sufficient to mitigate this issue. The total request size can also be limited by a proxy (e.g. nginx) in front of the actual application as a workaround. However, for applications that actually want to accept large file uploads via `multipart/form-data`, a simple size limit would not be practical. The multipart parser currently used by Litestar expects a single byte string as input and does not support incremental parsing via `Request.stream()`. Applications could bypass the Litestar parser and use a [streaming parser](https://pypi.org/project/multipart/) to read from `Request.stream()` instead, but that would not work with extractors and other features of the framework. Switching the parser for a different implementation is currently not possible via public APIs.

### PoC
Start an applications that accesses `Request.json()`, `Request.msgpack()` or `Request.form()` or uses an extractor that relies on those parsers internally, and send a large request with a matching content type. The actual content of the request does not matter. For example: `curl -F "foo=</dev/random" http://127.0.0.1:8000/`) for `multipart/form-data`. Server memory consumption will increase very quickly until memory (and swap) are exhausted.

### Impact
This is a denial of service (DoS) vulnerability affecting all Litestar applications that process json, msgpack or form-data submission requests.

## References
- https://github.com/litestar-org/litestar/security/advisories/GHSA-gjcc-jvgw-wvwj
- https://github.com/litestar-org/litestar/security/advisories/GHSA-p24m-863f-fm6q
- https://nvd.nist.gov/vuln/detail/CVE-2024-52581
- https://github.com/litestar-org/litestar/commit/53c1473b5ff7502816a9a339ffc90731bb0c2138
- https://github.com/litestar-org/litestar
- https://github.com/litestar-org/litestar/blob/main/litestar/_multipart.py#L97
- https://github.com/pypa/advisory-database/tree/main/vulns/litestar/PYSEC-2024-178.yaml
