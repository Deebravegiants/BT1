# [M] Open WebUI: `WEB_FETCH_FILTER_LIST` host allow/block filter bypassable via URL path and non-label-boundary matching

## Summary
Severity: Medium
Advisory: GHSA-qg3f-8x3j-ggf2
CVE: CVE-2026-59223
CWE: CWE-693
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-qg3f-8x3j-ggf2
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.10.0

## Details
## Summary

The administrator-configured `WEB_FETCH_FILTER_LIST` (the allow/block list applied to server-side web fetches: RAG URL ingestion, URL-to-markdown, web-search content fetch) matches hostnames incorrectly, so the filter can be bypassed.

## Details

`is_string_allowed` (`backend/open_webui/utils/misc.py`) matches with `str.endswith(...)`, and the primary web-fetch call site (`backend/open_webui/retrieval/web/utils.py`) called it with the **full URL string**, not the hostname:

- **Blocklist bypass via path.** A blocklist entry `!internal.example.com` only matches a URL that *ends with* that string. Any URL with a path (`https://internal.example.com/x`) ends with `/x`, so the entry never matches and the fetch proceeds. The blocklist effectively only stopped path-less URLs.
- **Allowlist false-reject and bypass.** An allowlist `company.com` rejected the legitimate `https://api.company.com/status` and admitted `https://attacker.example/path/company.com`.
- **Non-label-boundary matching** at the hostname-shaped call site (`retrieval/web/main.py`): `endswith('corp.com')` also matched `evilcorp.com`, and `10.0.0.1` matched `110.0.0.1`.

## Impact

An authenticated user able to trigger a server-side web fetch can reach hosts the administrator intended to block with `WEB_FETCH_FILTER_LIST`.

Open WebUI's primary SSRF protection is a separate, always-on guard that rejects any URL resolving to a non-global IP (`validate_url` and the connection-layer `_ssrf_safe_new_conn`, active whenever `ENABLE_RAG_LOCAL_WEB_FETCH` is off, the default). That guard is unaffected by this issue and continues to block loopback, RFC1918 and link-local addresses, including the `169.254.169.254` cloud-metadata endpoint. This bypass therefore does **not** grant access to those internal targets. What it defeats is the administrator's ability to block specific **publicly-resolvable** hosts (internal services reachable from the server over a public IP, e.g. split-horizon DNS or internal PaaS endpoints) and to enforce an allowlist. Fetched content is returned to the requester, so for hosts reachable from the server's network position this is a read/content-disclosure SSRF against the admin-blocked host.

## Patch

Matching is now performed on the parsed hostname using DNS label boundaries. A dedicated `is_host_allowed(host, ...)` matches an entry only when host and entry are equal or the entry is a parent domain (`host == entry or host.endswith('.' + entry)`), so `corp.com` matches `api.corp.com` but not `evilcorp.com`, and IP entries match only the identical address. Both web-fetch call sites pass the parsed hostname rather than the full URL. The generic `is_string_allowed` is retained unchanged for unrelated non-host filters.

## Credit

Reported by @addcontent.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-qg3f-8x3j-ggf2
- https://nvd.nist.gov/vuln/detail/CVE-2026-59223
- https://github.com/open-webui/open-webui/pull/25949
- https://github.com/open-webui/open-webui/commit/087878ce848a4d828012068b5997dac480f43656
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.10.0
