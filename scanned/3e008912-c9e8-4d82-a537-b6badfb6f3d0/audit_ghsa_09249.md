# [H] Prometheus exporter process crash via malformed HTTP request

## Summary
Severity: High
Advisory: GHSA-q7rr-3cgh-j5r3
CVE: CVE-2026-44902
CWE: CWE-755
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-q7rr-3cgh-j5r3
Type: github-advisory

## Affected
- npm: `@opentelemetry/exporter-prometheus` — affected >=0 <0.217.0
- npm: `@opentelemetry/sdk-node` — affected >=0 <0.217.0
- npm: `@opentelemetry/auto-instrumentations-node` — affected >=0 <0.75.0

## Details
## Summary

A single malformed HTTP request crashes any Node.js process running the OpenTelemetry JS Prometheus exporter. The metrics endpoint (default `0.0.0.0:9464`) has no error handling around URL parsing, so a request with an invalid URI causes an uncaught `TypeError` that terminates the process.

**You are affected by this vulnerability if either of the following apply to your application:**

* you directly use `@opentelemetry/exporter-prometheus` in your code through its built-in server.
* your `OTEL_METRICS_EXPORTER` environment variable includes `prometheus` **AND**
  * you use `@opentelemetry/sdk-node`
  * you use  `@opentelemetry/auto-instrumentations-node` via `--require @opentelemetry/auto-instrumentations-node/register`/`--import @opentelemetry/auto-instrumentations-node/register`

## Impact

**Denial of service.** Any application using the OpenTelemetry Prometheus exporter’s built-in server can be crashed by a single unauthenticated network packet sent to the metrics port. No authentication, special privileges, or prior access is required.

## Remediation

### Update to the fixed version

Update `@opentelemetry/exporter-prometheus` and `@opentelemetry/sdk-node` to version **0.217.0** or later. 
Update `@opentelemetry/auto-instrumentations-node` to version **0.75.0** or later.

This release adds proper error handling around the URL constructor, returning an HTTP `400` response on parse failure rather than allowing the exception to propagate and crash the process.

```
npm install @opentelemetry/exporter-prometheus@latest
```

### Do Not Expose the Endpoint to Untrusted Users

> [!IMPORTANT] 
> The following mitigations reduce exposure but do not fully remediate the vulnerability. Any client that *can* reach the metrics endpoint - including your own Prometheus scraper host if compromised - could still trigger the crash. Updating to **0.217.0** is the recommended resolution.

If updating is not immediately feasible, restrict access to the metrics endpoint so that it is not reachable by untrusted or unauthenticated network clients. For example:

* **Bind to localhost only** by setting the `host` option to `127.0.0.1` when configuring the `PrometheusExporter`, so the port is not exposed on public or shared network interfaces

* **Use a firewall or network policy** to restrict access to port `9464` (or whichever port you have configured) to only trusted Prometheus scrape hosts

* **Place the endpoint behind a reverse proxy** that filters or validates incoming requests before they reach the exporter

## Details

In `PrometheusExporter.ts`, the `_requestHandler` calls `new URL(request.url, this._baseUrl)` without any error handling. Node's HTTP parser accepts absolute-form URIs (e.g. `http://`) for proxy compatibility, including malformed ones. When `request.url` is `"http://"`, the `URL` constructor throws `TypeError: Invalid URL`. Since there is no try-catch in the handler, the exception propagates as an uncaught exception and crashes the process.

The Prometheus metrics endpoint is unauthenticated by design (Prometheus scrapes it) and binds to `0.0.0.0` by default, meaning it is reachable by any network client that can connect to the metrics port.

## Proof of Concept

Start any Node.js application with the Prometheus exporter running on the default port `9464`, then send a single raw TCP packet:

```
echo -ne 'GET http:// HTTP/1.1\r\nHost: localhost\r\n\r\n' | nc localhost 9464
```

The process crashes immediately with:

```
TypeError: Invalid URL
    at new URL (...)
    at PrometheusExporter._requestHandler (...)
```

## References
- https://github.com/open-telemetry/opentelemetry-js/security/advisories/GHSA-q7rr-3cgh-j5r3
- https://nvd.nist.gov/vuln/detail/CVE-2026-44902
- https://github.com/open-telemetry/opentelemetry-js
