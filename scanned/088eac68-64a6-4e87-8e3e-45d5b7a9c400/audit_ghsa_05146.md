# [C] Crawl4AI: Arbitrary file write (path traversal) in crawler downloads can lead to RCE

## Summary
Severity: Critical
Advisory: GHSA-2jq4-q6vv-4cp3
CWE: CWE-22, CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-2jq4-q6vv-4cp3
Type: github-advisory

## Affected
- PyPI: `crawl4ai` — affected >=0 <0.9.0

## Details
### Summary

When the crawler saves a downloaded file, the destination filename was taken from attacker-influenced input and joined to the downloads directory with no confinement. A filename containing an absolute path (e.g. `/etc/cron.d/evil`) or `../` traversal escaped the downloads directory, giving an arbitrary file write with attacker-controlled contents. Because the written bytes are attacker-controlled, this escalates to remote code execution (overwriting a shell rc-file, `~/.ssh/authorized_keys`, a cron entry, or a Python module on the import path).

### Affected paths

Two download sinks in `crawl4ai/async_crawler_strategy.py`:
- HTTP crawler (`AsyncHTTPCrawlerStrategy`): the filename is parsed from the response `Content-Disposition` header by `_extract_filename()` and written via `aiofiles.open(filepath, 'wb')`. Reachable directly via the SDK, and via the unauthenticated Docker `/crawl` endpoint when an `HTTPCrawlerConfig` is supplied.
- Browser crawler (`AsyncPlaywrightCrawlerStrategy`): the download's `suggested_filename` (controllable by the visited page) is joined to `downloads_path` and written via `download.save_as()`.

The HTTP-strategy sink is reachable pre-auth on the default Docker deployment; both are reachable for SDK users simply by crawling an attacker-controlled URL. The default Playwright crawl path that does not trigger a download is unaffected.

### Impact

Arbitrary file write with attacker-controlled content as the user running the crawler, escalating to remote code execution.

### Fix

Both sinks now resolve the destination through a single hardened helper (`_safe_download_filepath`) that reduces the attacker-influenced name to a bare basename (dropping absolute paths and `..` components) and re-checks, via `realpath`, that the resolved path stays inside the downloads root (defeating symlink/TOCTOU escapes). A traversal attempt is rejected; normal downloads are unchanged.

### Workarounds

- Upgrade to the patched version (0.9.0).
- Run the crawler as an unprivileged user with a dedicated, isolated downloads directory on a volume with no sensitive paths writable.
- Enable authentication (`CRAWL4AI_API_TOKEN`) on the Docker server.

### Credits

Y4tacker - reported the Content-Disposition path traversal in the HTTP crawler with a clear PoC and a basename + realpath-containment fix recommendation.

## References
- https://github.com/unclecode/crawl4ai/security/advisories/GHSA-2jq4-q6vv-4cp3
- https://github.com/unclecode/crawl4ai
