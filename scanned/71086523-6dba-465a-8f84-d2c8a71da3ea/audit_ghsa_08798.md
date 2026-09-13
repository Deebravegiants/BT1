# [H] python-multipart has Denial of Service via unbounded multipart part headers

## Summary
Severity: High
Advisory: GHSA-pp6c-gr5w-3c5g
CVE: CVE-2026-42561
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-pp6c-gr5w-3c5g
Type: github-advisory

## Affected
- PyPI: `python-multipart` — affected >=0 <0.0.27

## Details
### Summary

`python-multipart` has a denial of service vulnerability in multipart part header parsing. When parsing `multipart/form-data`, `MultipartParser` previously had no limit on the number of part headers or the size of an individual part header. An attacker could send a request with either many repeated headers without terminating the header block or a single very large header value, causing excessive CPU work before request rejection or completion.

### Impact

Applications that parse attacker-controlled `multipart/form-data` with affected versions of `python-multipart` can experience CPU exhaustion. ASGI applications using Starlette, FastAPI, or other frameworks that invoke `python-multipart` may have worker or event-loop delays while processing malicious upload requests.

### Details

The affected parser states are `HEADER_FIELD_START`, `HEADER_FIELD`, `HEADER_VALUE_START`, `HEADER_VALUE`, and `HEADER_VALUE_ALMOST_DONE`. The issue can be triggered by:

- A multipart part with an oversized individual header value.
- A multipart part with many repeated header lines or an unterminated header block.

Both variants are addressed by enforcing default parser limits for maximum header count and maximum header size.

### Mitigation

Upgrade to `python-multipart` `0.0.27` or later.

If upgrading is not immediately possible, reduce exposure by enforcing request body size limits at the server, proxy, or framework layer. This is only a mitigation; affected versions of `python-multipart` still parse multipart part headers without the default header count and header size limits.

## References
- https://github.com/Kludex/python-multipart/security/advisories/GHSA-pp6c-gr5w-3c5g
- https://nvd.nist.gov/vuln/detail/CVE-2026-42561
- https://github.com/Kludex/python-multipart
