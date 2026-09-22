# [H] Ech0 has Unauthenticated Server-Side Request Forgery in Website Preview Feature

## Summary
Severity: High
Advisory: GHSA-wc4h-2348-jc3p
CVE: CVE-2026-35036
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-wc4h-2348-jc3p
Type: github-advisory

## Affected
- Go: `github.com/lin-snow/ech0` — affected >=0 <1.4.8-0.20260401031029-4ca56fea5ba4

## Details
### Summary

Ech0 implements **link preview** (editor fetches a page title) through **`GET /api/website/title`**. That is **legitimate product behavior**, but the implementation is **unsafe**: the route is **unauthenticated**, accepts a **fully attacker-controlled URL**, performs a **server-side GET**, reads the **entire response body** into memory (`io.ReadAll`). There is **no** host allowlist, **no** SSRF filter, and **`InsecureSkipVerify: true`** on the outbound client.

**Attacker outcome :** Anyone who can reach the instance can **force the Ech0 server** to open **HTTP/HTTPS URLs of their choice** as seen from the **server’s network position** (Docker bridge, VPC, localhost from the process view). 
Go’s default `http.Client` **follows redirects** (unless disabled). Redirect chains can move the server-side request from an allowed-looking host to an internal target; the code does not disable this in `SendRequest`.

### Affected Components

**Ech0 codebase:**

- `internal/handler/common/common.go`  
  Handles the `/api/website/title` endpoint and accepts user-controlled URL input.

- `internal/service/common/common.go`  
  Processes the request and invokes the outbound HTTP fetch (`GetWebsiteTitle`).

- `internal/util/http/http.go`  
  Performs the HTTP request (`SendRequest`) with the following insecure configurations:
  - No URL validation or allowlist
  - Redirects enabled (default client behavior)
  - `InsecureSkipVerify: true`

### PoC 

**Environment:** Ech0 listening on `http://127.0.0.1:6277` (e.g. Docker image `sn0wl1n/ech0:latest`). No cookies or `Authorization` header.

**Step 1 — baseline: unauthenticated server-side fetch (public URL):**

```bash
curl.exe -sS -m 20 "http://127.0.0.1:6277/api/website/title?website_url=https://example.com"
```

**Observed result (verified):** HTTP 200, JSON with `code: 1` and `data` **`Example Domain`** — proves the **Ech0 process** performed an outbound GET without any client auth.

**Step 2 — impact: host-bound page + recorded leak (repo PoC file)**
Committed PoC page: **`poc_ssrf_proof.html`** 

1. From **`poc file directory`**, listen on **0.0.0.0** (port **9999**):

```bash
python -m http.server 9999 --bind 0.0.0.0
```

2. **Docker Desktop (Windows / macOS):** Ech0 in Docker fetches the host via `host.docker.internal`:

```bash
curl.exe -sS -m 20 "http://127.0.0.1:6277/api/website/title?website_url=http://host.docker.internal:9999/poc_ssrf_proof.html"
```

**Recorded response (verified this workspace, Ech0 4.2.2 in Docker):**

```json
{"code":1,"msg":"获取网站标题成功","data":"ECH0_SSRF_POC_LEAK_2026"}
```

**Python server log:** `GET /poc_ssrf_proof.html` → **200** (proves the **server/container** pulled the page from your host).

**Leak channel:** the backend **reads the full HTML body** before parsing (see `io.ReadAll` in `SendRequest`).


### Impact

- **Verified:** Unauthenticated callers can make the Ech0 process issue **server-side HTTP(S) requests** to **internal/reserved targets** reachable from that process (PoC Step 2: host-reachable listener reflected in JSON).
- **Code-level:** The full response is **read into memory** (`io.ReadAll`); only the title string is returned. Combined with **default HTTP redirect following** (standard `http.Client` behavior; not disabled here), the effective request graph is larger than a single URL.
- **TLS:** `InsecureSkipVerify: true` means **misissued or intercepted TLS** to internal HTTPS services is still accepted from the server’s perspective.
- **Deployment-dependent:** Where routing allows (typical cloud VMs), **`169.254.169.254`-class** endpoints are in scope for the **same code path**; treat as **high*.
- **DOS(Denial of Service)**: reading the whole body into memory with io.ReadAll is a DoS vector if you point it at a massive file.


## Remediation

- Enforce **SSRF-safe URL policy**: allow only needed schemes/hosts; block link-local, metadata, and loopback unless explicitly required.
- Remove **`InsecureSkipVerify`**; use normal TLS verification.
- **Limit redirects** (disable or cap hops; re-validate each target).
- Add **response size / timeout** limits; optionally restrict egress at the **network** layer.

## References
- https://github.com/lin-snow/Ech0/security/advisories/GHSA-wc4h-2348-jc3p
- https://nvd.nist.gov/vuln/detail/CVE-2026-35036
- https://github.com/lin-snow/Ech0
