# [H] aiohttp vulnerable to Denial of Service when trying to parse malformed POST requests

## Summary
Severity: High
Advisory: GHSA-5m98-qgg9-wh84
CVE: CVE-2024-30251
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-05-03
Source: https://github.com/advisories/GHSA-5m98-qgg9-wh84
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.9.4

## Details
### Summary
An attacker can send a specially crafted POST (multipart/form-data) request. When the aiohttp server processes it, the server will enter an infinite loop and be unable to process any further requests.

### Impact
An attacker can stop the application from serving requests after sending a single request.

-------

For anyone needing to patch older versions of aiohttp, the minimum diff needed to resolve the issue is (located in `_read_chunk_from_length()`):

```diff
diff --git a/aiohttp/multipart.py b/aiohttp/multipart.py
index 227be605c..71fc2654a 100644
--- a/aiohttp/multipart.py
+++ b/aiohttp/multipart.py
@@ -338,6 +338,8 @@ class BodyPartReader:
         assert self._length is not None, "Content-Length required for chunked read"
         chunk_size = min(size, self._length - self._read_bytes)
         chunk = await self._content.read(chunk_size)
+        if self._content.at_eof():
+            self._at_eof = True
         return chunk
 
     async def _read_chunk_from_stream(self, size: int) -> bytes:
```

This does however introduce some very minor issues with handling form data. So, if possible, it would be recommended to also backport the changes in:
https://github.com/aio-libs/aiohttp/commit/cebe526b9c34dc3a3da9140409db63014bc4cf19
https://github.com/aio-libs/aiohttp/commit/7eecdff163ccf029fbb1ddc9de4169d4aaeb6597
https://github.com/aio-libs/aiohttp/commit/f21c6f2ca512a026ce7f0f6c6311f62d6a638866

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-5m98-qgg9-wh84
- https://nvd.nist.gov/vuln/detail/CVE-2024-30251
- https://github.com/aio-libs/aiohttp/commit/7eecdff163ccf029fbb1ddc9de4169d4aaeb6597
- https://github.com/aio-libs/aiohttp/commit/cebe526b9c34dc3a3da9140409db63014bc4cf19
- https://github.com/aio-libs/aiohttp/commit/f21c6f2ca512a026ce7f0f6c6311f62d6a638866
- https://github.com/aio-libs/aiohttp
- https://lists.debian.org/debian-lts-announce/2025/02/msg00002.html
- http://www.openwall.com/lists/oss-security/2024/05/02/4
