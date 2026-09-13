# [H] Mistune: Denial of Service — RecursionError via Excessive Emphasis Markers in Markdown

## Summary
Severity: High
Advisory: GHSA-6m44-fpc8-c3rq
CVE: CVE-2026-76098
CWE: CWE-674
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-6m44-fpc8-c3rq
Type: github-advisory

## Affected
- PyPI: `mistune` — affected >=3.3.0 <3.3.3

## Details
## Summary
Mistune v3.3.2 is vulnerable to a Denial of Service (DoS) attack via uncontrolled recursion in the HTML rendering of deeply-nested emphasis tokens. By submitting Markdown containing approximately 1,000 consecutive asterisk characters, an attacker causes the Python process to crash with RecursionError.

## Details
The InlineParser's _process_emphasis_delimiters() creates deeply nested <strong> tokens from consecutive emphasis markers (every 2 asterisks add one nesting level). With 1,000 consecutive asterisks, approximately 500 levels of nesting are produced. The HTMLRenderer.render_token() method (src/mistune/renderers/html.py:40-57) renders these tokens recursively: when a token has children, line 48 calls self.render_tokens(token['children'], state), entering child rendering. Each nesting level produces ~2 stack frames, so 500 levels ≈ 1,000 frames, exceeding Python's default recursion limit (sys.getrecursionlimit() = 1000). The emphasis() and strong() methods (lines 80-84) wrap recursively rendered child content in <em> and <strong> tags, perpetuating the recursion. This vulnerability affects all mistune APIs including markdown() and html().

Core vulnerable code path:

```python
# src/mistune/renderers/html.py:40-57
def render_token(self, token: Dict[str, Any], state: BlockState) -> str:
    func = self._get_method(token["type"])
    attrs = token.get("attrs")
    if "raw" in token:
        text = token["raw"]
    elif "children" in token:
        text = self.render_tokens(token["children"], state)
    else:
        if attrs:
            return func(**attrs)
        else:
            return func()
    if attrs:
        return func(text, **attrs)
    else:
        return func(text)
```

The recursive call to render_tokens() on line 48 processes nested child tokens. With 500 levels of nested emphasis/strong tokens, this recursion exceeds Python's default recursion limit of 1000, causing a RecursionError.

```python
# src/mistune/renderers/html.py:80-84
def emphasis(self, text: str) -> str:
    return "<em>" + text + "</em>"

def strong(self, text: str) -> str:
    return "<strong>" + text + "</strong>"
```

The emphasis() and strong() methods wrap their text content (which is itself the recursively-rendered output of nested child tokens) in HTML tags, creating the chain of recursion: each call to strong() includes rendered children that themselves call strong(), etc.

## POC

``` wiki
from mistune import html

payload = '*' * 1000
try:
    result = html(payload)
    print('No crash - recursion handled')
except RecursionError as e:
    print(f'[VULN] RecursionError: {e} - Process would crash!')
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
```

<img width="1139" height="664" alt="1" src="https://github.com/user-attachments/assets/d2095b9f-0a6a-4bef-8013-cbc6946cf8f1" />



## Impact
CVSS 3.1: 7.5 (High) — AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H. An attacker can crash any server process using mistune with approximately 2KB of Markdown input. In web applications, this can be triggered through user-generated content such as forum posts or comments, causing denial of service for all concurrent users sharing the same Python process. Both mistune.markdown() and mistune.html() are affected.

## Remediation
1. Add a maximum nesting depth limit in the emphasis parsing stage, similar to BlockParser's max_nested_level mechanism (currently at DEFAULT_MAX_NESTED_LEVEL = 20). When the limit is exceeded, treat excess emphasis markers as literal text. 2. Alternatively, refactor HTMLRenderer to use an explicit stack-based iterative approach instead of recursive calls for rendering nested tokens. 3. As a defense-in-depth measure, document the recursion risk and recommend that applications deploying mistune set a higher recursion limit or implement request-level timeouts.

## References
- https://github.com/lepture/mistune/security/advisories/GHSA-6m44-fpc8-c3rq
- https://nvd.nist.gov/vuln/detail/CVE-2026-76098
- https://github.com/lepture/mistune/commit/0938fb781d0aded99de801b340ec1f8debeae5b2
- https://github.com/lepture/mistune
- https://github.com/lepture/mistune/releases/tag/v3.3.3
