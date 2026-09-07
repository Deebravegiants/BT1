# [M] Prometheus has Stored XSS via metric names and label values in Prometheus web UI tooltips and metrics explorer

## Summary
Severity: Medium
Advisory: GHSA-vffh-x6r8-xx99
CVE: CVE-2026-40179
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-13
Source: https://github.com/advisories/GHSA-vffh-x6r8-xx99
Type: github-advisory

## Affected
- Go: `github.com/prometheus/prometheus` — affected >=3.0.0
- Go: `github.com/prometheus/prometheus` — affected >=3.6.0
- Go: `github.com/prometheus/prometheus` — affected >=0 <0.311.2-0.20260410083055-07c6232d159b

## Details
### Impact

Stored cross-site scripting (XSS) via crafted metric names in the Prometheus web UI:

* **Old React UI + New Mantine UI:** When a user hovers over a chart tooltip on the Graph page, metric names containing HTML/JavaScript are injected into `innerHTML` without escaping, causing arbitrary script execution in the user's browser.
* **Old React UI only:** When a user opens the Metric Explorer (globe icon next to the PromQL expression input field), and a metric name containing HTML/JavaScript is rendered in the fuzzy search results, it is injected into `innerHTML` without escaping, causing arbitrary script execution in the user's browser.
* **Old React UI only:** When a user views a heatmap chart and hovers over a cell, the `le` label values of the underlying histogram buckets are interpolated into `innerHTML` without escaping. While `le` is conventionally a numeric bucket boundary, Prometheus does not enforce this — arbitrary UTF-8 strings are accepted as label values, allowing script injection via a crafted scrape target or remote write.

With Prometheus v3.x defaulting to UTF-8 metric and label name validation, characters like `<`, `>`, and `"` are now valid in metric names and labels, making this exploitable.

An attacker who can inject metrics (via a compromised scrape target, remote write, or OTLP receiver endpoint) can execute JavaScript in the browser of any Prometheus user who views the metric in the Graph UI. From the XSS context, an attacker could for example:

- Read `/api/v1/status/config` to extract sensitive configuration (although credentials / secrets are redacted by the server)
- Call `/-/quit` to shut down Prometheus (only if `--web.enable-lifecycle` is set)
- Call `/api/v1/admin/tsdb/delete_series` to delete data (only if `--web.enable-admin-api` is set)
- Exfiltrate metric data to an external server

Both the new Mantine UI and the old React UI are affected. The vulnerable code paths are:

- `web/ui/mantine-ui/src/pages/query/uPlotChartHelpers.ts` — tooltip `innerHTML` with unescaped `labels.__name__`
- `web/ui/react-app/src/pages/graph/GraphHelpers.ts` — tooltip content with unescaped `labels.__name__`
- `web/ui/react-app/src/pages/graph/MetricsExplorer.tsx` — fuzzy search results rendered via `dangerouslySetInnerHTML` without sanitization
- `web/ui/react-app/src/vendor/flot/jquery.flot.heatmap.js` — heatmap tooltip with unescaped label values

### Patches

A patch has been published in Prometheus 3.5.2 LTS and Prometheus 3.11.2. The fix applies `escapeHTML()` to all user-controlled values (metric names and label values) before inserting them into `innerHTML`. This advisory will be updated with the patched version once released.

### Workarounds

- If using the remote write receiver (`--web.enable-remote-write-receiver`), ensure it is not exposed to untrusted sources.
- If using the OTLP receiver (`--web.enable-otlp-receiver`), ensure it is not exposed to untrusted sources.
- Ensure scrape targets are trusted and not under attacker control.
- Do not enable admin / mutating API endpoints (e.g. `--web.enable-admin-api` or `web.enable-lifecycle`) in cases where you cannot prevent untrusted data from being ingested.
- Users should avoid clicking untrusted links, especially those containing functions such as label_replace, as they may generate poisoned label names and values.

### Acknowledgements

Thanks to @gladiator9797 (Duc Anh Nguyen from TinyxLab) for reporting this.

## References
- https://github.com/prometheus/prometheus/security/advisories/GHSA-vffh-x6r8-xx99
- https://nvd.nist.gov/vuln/detail/CVE-2026-40179
- https://github.com/prometheus/prometheus/pull/18506
- https://github.com/prometheus/prometheus/commit/07c6232d159bfb474a077788be184d87adcfac3c
- https://github.com/prometheus/prometheus
