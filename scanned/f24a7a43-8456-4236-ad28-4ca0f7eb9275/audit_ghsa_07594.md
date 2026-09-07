# [M] NiceGUI's XSS vulnerability in ui.markdown() allows arbitrary JavaScript execution through unsanitized HTML content

## Summary
Severity: Medium
Advisory: GHSA-v82v-c5x8-w282
CVE: CVE-2026-25516
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-v82v-c5x8-w282
Type: github-advisory

## Affected
- PyPI: `nicegui` — affected >=0 <3.7.0

## Details
## Description

The `ui.markdown()` component uses the `markdown2` library to convert markdown content to HTML, which is then rendered via `innerHTML`. By default, `markdown2` allows raw HTML to pass through unchanged. This means that if an application renders user-controlled content through `ui.markdown()`, an attacker can inject malicious HTML containing JavaScript event handlers.

Unlike other NiceGUI components that render HTML (`ui.html()`, `ui.chat_message()`, `ui.interactive_image()`), the `ui.markdown()` component does not provide or require a `sanitize` parameter, leaving applications vulnerable to XSS attacks.

## Proof of Concept

```python
from nicegui import ui

# User-controlled input containing malicious payload
user_input = 'Hello! <img src=x onerror="alert(\'XSS\')">'

ui.markdown(user_input)  # XSS executes when page loads

ui.run()
```

When this page loads, the JavaScript in the `onerror` handler executes, potentially allowing an attacker to:
- Steal session cookies or authentication tokens
- Perform actions on behalf of the user
- Redirect users to malicious sites
- Modify page content

## Impact

Applications that render user-provided content through `ui.markdown()` are vulnerable to stored or reflected XSS attacks. This is particularly concerning for:
- Chat applications displaying user messages
- CMS or documentation systems with user-editable content
- Any application that displays markdown from untrusted sources

## Remediation

A release has been published in version 3.7.0.

### For Users (Immediate Workaround)

Until a fix is released, **do not pass untrusted content directly to `ui.markdown()`**. Instead, use one of these approaches:

**Option 1: Convert and sanitize manually using `ui.html()`**

```python
import markdown2
from html_sanitizer import Sanitizer

sanitizer = Sanitizer()

def safe_markdown(content: str) -> None:
    """Render markdown with HTML sanitization."""
    html = markdown2.markdown(content)
    ui.html(sanitizer.sanitize(html), sanitize=False)

# Usage
safe_markdown(user_input)
```

**Option 2: Escape HTML before markdown conversion (if raw HTML not needed)**

```python
import html

# Escape HTML entities - prevents any HTML from being interpreted
ui.markdown(html.escape(user_input))
```

### Proposed Fix

Add a `sanitize` parameter to `ui.markdown()` consistent with other HTML-rendering components, and/or add an `escape_html` parameter.

## References
- https://github.com/zauberzeug/nicegui/security/advisories/GHSA-v82v-c5x8-w282
- https://nvd.nist.gov/vuln/detail/CVE-2026-25516
- https://github.com/zauberzeug/nicegui/commit/f1f7533577875af7d23f161ed3627f73584cb561
- https://github.com/zauberzeug/nicegui
