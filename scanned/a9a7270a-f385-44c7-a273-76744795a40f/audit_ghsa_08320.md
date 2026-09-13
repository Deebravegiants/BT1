# [M] NiceGUI: Unauthenticated log-volume denial of service in dynamic resource routes

## Summary
Severity: Medium
Advisory: GHSA-pq7c-x8g4-rvp6
CVE: CVE-2026-45554
CWE: CWE-248, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-pq7c-x8g4-rvp6
Type: github-advisory

## Affected
- PyPI: `nicegui` — affected >=0 <3.12.0

## Details
### Summary

Two FastAPI routes that serve per-component static assets in NiceGUI accept a sub-path parameter that may resolve to a directory rather than a file. Requests that resolve to a directory raise an unhandled `RuntimeError` inside Starlette's `FileResponse`, which Uvicorn writes to the server log as a full traceback. Because the routes are reachable without authentication, a remote attacker can amplify log volume and consume disk and log-pipeline capacity on any publicly reachable NiceGUI server. There is no impact to confidentiality or integrity.

### Details

The affected routes are the per-component **resource** route (added in v1.4.6) and the **ESM module** route (added in v3.0.0). Both join a user-supplied path segment with a registered base directory and pass the result to `FileResponse`. The existing existence check uses `pathlib.Path.exists()`, which returns `True` for directories — so a request whose sub-path resolves to a directory passes the guard and triggers an unhandled exception inside Starlette.

FastAPI has no default handler for `RuntimeError`, so each such request results in a 500 response and a multi-frame traceback in the server log.

Other NiceGUI-served paths (`/static/...`, `/components/...`, `/libraries/...`) are not affected; they do not use the same sub-path-to-`FileResponse` pattern.

### Impact

A remote, unauthenticated attacker can repeatedly trigger the error condition with crafted requests. Each request emits roughly 100 lines of traceback in a default setup, and more when additional middleware layers are present. At sustained request rates this can:

- exhaust disk space on hosts with default log retention,
- saturate downstream log-shipping pipelines,
- generate alert fatigue or mask other events in monitoring.

There is no remote code execution, no path traversal, and no data exposure beyond the absolute installation path that already appears in any uncaught exception trace.

### Workarounds

For deployments that cannot upgrade immediately:

- Place NiceGUI behind a reverse proxy that rejects requests where the path after `/_nicegui/<version>/esm/<key>/` or `/_nicegui/<version>/resources/<key>/` is empty.
- Rate-limit the `/_nicegui/` prefix at the proxy.
- Configure log rotation aggressively for the affected service.

## References
- https://github.com/zauberzeug/nicegui/security/advisories/GHSA-pq7c-x8g4-rvp6
- https://nvd.nist.gov/vuln/detail/CVE-2026-45554
- https://github.com/zauberzeug/nicegui
- https://github.com/zauberzeug/nicegui/releases/tag/v3.12.0
