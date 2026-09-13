# [H] Denial of service vulnerability when parsing multipart request body

## Summary
Severity: High
Advisory: GHSA-p24m-863f-fm6q
CVE: CVE-2023-25578
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-15
Source: https://github.com/advisories/GHSA-p24m-863f-fm6q
Type: github-advisory

## Affected
- PyPI: `starlite` — affected >=0 <1.51.2

## Details
### Summary

The request body parsing in `starlite` allows a potentially unauthenticated
 attacker to consume a large amount of CPU time and RAM.

### Details

The multipart body parser processes an unlimited number of file parts.
The multipart body parser processes an unlimited number of field parts.

### Impact

This is a remote, potentially unauthenticated Denial of Service vulnerability.

This vulnerability affects applications with a request handler that accepts
 a `Body(media_type=RequestEncodingType.MULTI_PART)`.

The large amount of CPU time required for processing requests can block all
 available worker processes and significantly delay or slow down the processing
 of legitimate user requests.
The large amount of RAM accumulated while processing requests can lead to
 Out-Of-Memory kills.
Complete DoS is achievable by sending many concurrent multipart requests in a
 loop.

## References
- https://github.com/starlite-api/starlite/security/advisories/GHSA-p24m-863f-fm6q
- https://nvd.nist.gov/vuln/detail/CVE-2023-25578
- https://github.com/starlite-api/starlite/commit/9674fe803628f986c03fe60769048cbc55b5bf83
- https://github.com/pypa/advisory-database/tree/main/vulns/starlite/PYSEC-2023-49.yaml
- https://github.com/starlite-api/starlite
- https://github.com/starlite-api/starlite/releases/tag/v1.51.2
