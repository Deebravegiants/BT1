# [H] AIOHTTP: Out-of-bounds heap read in C HTTP response parser error path (malformed chunked response)

## Summary
Severity: High
Advisory: GHSA-cq5v-8q36-5273
CVE: CVE-2026-69244
CWE: CWE-125, CWE-400, CWE-416
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-cq5v-8q36-5273
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.14.3

## Details
### Summary

An out-of-bounds heap read could occur in the C response parser while building an error message for a malformed response.

### Impact

An attacker controlled server, or possibly an accidental response could trigger a DoS in the client.

### Workaround

If unable to upgrade, the Python parser is unaffected and can be used with `AIOHTTP_NO_EXTENSIONS=1`.

---

Patch: https://github.com/aio-libs/aiohttp/commit/49f65d54150397892f7bcc4aae887767d51c322d

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-cq5v-8q36-5273
- https://github.com/aio-libs/aiohttp/pull/13223
- https://github.com/aio-libs/aiohttp/commit/49f65d54150397892f7bcc4aae887767d51c322d
- https://github.com/aio-libs/aiohttp
- https://github.com/aio-libs/aiohttp/releases/tag/v3.14.3
