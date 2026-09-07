# [M] PraisonAI Vulnerable to Stored XSS via Unsanitized Agent Output in HTML Rendering (nh3 Not a Required Dependency)

## Summary
Severity: Medium
Advisory: GHSA-cfg2-mxfj-j6pw
CVE: CVE-2026-40112
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-cfg2-mxfj-j6pw
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.5.128

## Details
## Summary

The Flask API endpoint in `src/praisonai/api.py` renders agent output as HTML without effective sanitization. The `_sanitize_html` function relies on the `nh3` library, which is not listed as a required or optional dependency in `pyproject.toml`. When `nh3` is absent (the default installation), the sanitizer is a no-op that returns HTML unchanged. An attacker who can influence agent input (via RAG data poisoning, web scraping results, or prompt injection) can inject arbitrary JavaScript that executes in the browser of anyone viewing the API output.

## Details

In `src/praisonai/api.py`, lines 6-14 define the sanitizer with a try/except ImportError fallback:

```python
try:
    import nh3
    def _sanitize_html(html: str) -> str:
        return nh3.clean(html)
except ImportError:
    def _sanitize_html(html: str) -> str:
        """Fallback: no nh3, return as-is (install nh3 for XSS protection)."""
        return html
```

The `home()` route at lines 21-25 converts agent output to HTML via `markdown.markdown()` (which preserves raw HTML tags by default) and embeds it in an HTML response using an f-string — bypassing Flask's Jinja2 auto-escaping:

```python
@app.route('/')
def home():
    output = basic()
    html_output = _sanitize_html(markdown.markdown(str(output)))
    return f'<html><body>{html_output}</body></html>'
```

Since `nh3` is not in any dependency list (`pyproject.toml` core deps, optional deps, or requirements files), a standard installation will always hit the fallback path. The `markdown` library's default behavior passes through raw HTML tags in input text, so any `<script>` or event handler attributes in the agent output flow directly into the response.

Additionally, `deploy.py:76-91` generates a deployment version of `api.py` that has **no sanitization at all** — it directly calls `markdown.markdown(output)` without any `_sanitize_html` wrapper.

## PoC

1. Set up a PraisonAI instance with an agent that processes external content (e.g., web scraping or RAG retrieval):

```yaml
# agents.yaml
framework: crewai
topic: test
roles:
  researcher:
    role: Researcher
    goal: Process user-provided content
    backstory: You process content exactly as given
    tasks:
      process:
        description: "Return this exact text: <img src=x onerror=alert(document.cookie)>"
        expected_output: The text as-is
```

2. Verify `nh3` is not installed (default):
```bash
pip show nh3 2>&1 | grep -c "not found"
# Returns 1 (not installed)
```

3. Start the API:
```bash
python src/praisonai/api.py
```

4. Access the endpoint:
```bash
curl http://localhost:5000/
```

5. Response contains unsanitized HTML:
```html
<html><body><p><img src=x onerror=alert(document.cookie)></p></body></html>
```

6. Opening this in a browser executes the JavaScript payload.

## Impact

- **Session hijacking**: An attacker can steal cookies or session tokens from users viewing the API output.
- **Credential theft**: Injected scripts can present fake login forms or exfiltrate data to attacker-controlled servers.
- **Actions on behalf of users**: Malicious JavaScript can perform actions in the context of the victim's browser session.

The attack surface includes any scenario where agent output contains attacker-influenced content: RAG retrieval from poisoned documents, web scraping of malicious pages, processing of adversarial user prompts, or multi-agent communication where one agent's output is tainted.

## Recommended Fix

Make `nh3` a required dependency when using the API, and remove the silent fallback:

```python
# Option 1: Make nh3 required in pyproject.toml under the "api" optional dependency
# In pyproject.toml:
# api = [
#     "flask>=3.0.0",
#     ...
#     "nh3>=0.2.14",
# ]

# Option 2: Use markdown's built-in HTML stripping as a safe default
import markdown

def _sanitize_html(html: str) -> str:
    try:
        import nh3
        return nh3.clean(html)
    except ImportError:
        import re
        return re.sub(r'<[^>]+>', '', html)  # Strip all HTML tags as fallback

# Option 3 (preferred): Use Flask's Jinja2 templating with auto-escaping
# instead of f-string interpolation, or use markupsafe.escape()
from markupsafe import Markup

@app.route('/')
def home():
    output = basic()
    # Use markdown with safe extensions only
    html_output = markdown.markdown(str(output), extensions=[])
    try:
        import nh3
        html_output = nh3.clean(html_output)
    except ImportError:
        raise RuntimeError("nh3 is required for safe HTML rendering. Install with: pip install nh3")
    return f'<html><body>{html_output}</body></html>'
```

Also fix `deploy.py:76-91` to include sanitization in the generated `api.py`.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-cfg2-mxfj-j6pw
- https://nvd.nist.gov/vuln/detail/CVE-2026-40112
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.5.128
