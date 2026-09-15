# [H] Open WebUI: SSRF Protection Bypass in Playwright Web Loader via HTTP Redirects

## Summary
Severity: High
Advisory: GHSA-jrfp-m64g-pcwv
CVE: CVE-2026-54018
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-jrfp-m64g-pcwv
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.6

## Details
### Summary
The SafePlaywrightURLLoader implements a validate_url function to prevent SSRF attacks by checking the IP address of the user-provided URL. However, this validation is performed only on the initial URL.

Since Playwright automatically follows HTTP redirects (301/302) by default, an attacker can bypass the validation by providing a safe URL that redirects to a restricted internal network address (e.g., localhost, Docker container network, or Cloud Metadata).

This allows the application to access internal services despite ENABLE_RAG_LOCAL_WEB_FETCH being set to False

### Details
Root Cause

The application validates the initial user-provided URL using self._safe_process_url_sync(url). This correctly resolves the domain and ensures it does not point to a private IP.

The application then calls page.goto(url). By default, Playwright automatically follows HTTP redirects (301/302).

The Bypass: If the destination server returns a redirect to an internal IP (e.g., 127.0.0.1 or 169.254.169.254), the browser follows it without re-validating the new destination. The initial validation is bypassed because it only checked the first URL, not the entire redirect chain.

```python
for url in self.urls:
    try:
        self._safe_process_url_sync(url)  
        page = browser.new_page()
        response = page.goto(url, timeout=self.playwright_timeout)  #this
        if response is None:
            raise ValueError(...)
        text = self.evaluator.evaluate(page, browser, response)
```

### PoC
(This PoC uses Docker to easily demonstrate internal network access (accessing a container by service name). However, the vulnerability is NOT tied to Docker.)

1. Ensure the Open WebUI is configured with the following environment variables. The vulnerability is specific to the Playwright engine.
2. ENABLE_RAG_LOCAL_WEB_FETCH=False (Default)
3. RAG_WEB_LOADER_ENGINE=playwright
4. Setup and run attack server
5. In Open WebUI, use the "Web Search" or "URL Loader" feature.
6. Input the attacker's URL (e.g., http://attacker-ip/).

```python
# attack_server.py
from flask import Flask, redirect
app = Flask(__name__)

@app.route('/')
def attack():
    # Redirect to the Open WebUI container's internal port
    return redirect("http://open-webui:8080/api/version", code=302)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
```
<img width="580" height="192" alt="image" src="https://github.com/user-attachments/assets/4600dbb5-a81d-4e58-b787-afe04fe59d6e" />

The Playwright browser follows the redirect to the internal address (http://open-webui:8080/api/version)

### Impact
+ Cloud Environments: Access to Instance Metadata Service (IMDS) to steal cloud credentials.
+ Intranet/On-Premise: Scanning internal networks and accessing unauthenticated internal tools.
+ Container Environments: Accessing other containers within the same network.

### Recommended Patch
implement a request interceptor using Playwright's page.route. This ensures all requests, including redirects, are validated before connection.

apply the following logic to both lazy_load and alazy_load methods:

```python
# async context
async def intercept_route(route):
    try:
        await run_in_threadpool(validate_url, route.request.url)
        await route.continue_()
    except Exception:
        await route.abort()

await page.route("**/*", intercept_route)
response = await page.goto(url, timeout=self.playwright_timeout)
```

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-jrfp-m64g-pcwv
- https://nvd.nist.gov/vuln/detail/CVE-2026-54018
- https://github.com/advisories/GHSA-jrfp-m64g-pcwv
- https://github.com/open-webui/open-webui
- https://github.com/pypa/advisory-database/tree/main/vulns/open-webui/PYSEC-2026-2743.yaml
- https://pypi.org/project/open-webui
