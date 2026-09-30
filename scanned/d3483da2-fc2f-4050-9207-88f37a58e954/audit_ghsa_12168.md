# [H] Uncontrolled recursion DoS in JustHTML() via deeply nested HTML

## Summary
Severity: High
Advisory: GHSA-v7cf-c9rm-wm3j
CVE: CVE-2026-9769
CWE: CWE-674
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-v7cf-c9rm-wm3j
Type: github-advisory

## Affected
- PyPI: `justhtml` — affected >=0 <1.10.0

## Details
### Summary

justhtml through 1.9.1 allows denial of service via deeply nested HTML. During parsing, `JustHTML.__init__()` always reaches `TreeBuilder.finish()`, which unconditionally calls `_populate_selectedcontent()`. That function recursively traverses the DOM via `_find_elements()` / `_find_element()` without a depth bound, allowing attacker-controlled deeply nested input to trigger an unhandled `RecursionError` on CPython. Depending on the host application's exception handling, this can abort parsing, fail requests, or terminate a worker/process.

### Details

`TreeBuilder.finish()` ([`treebuilder.py#L476`](https://github.com/EmilStenstrom/justhtml/blob/a866b6077770d9ec4cb6b6f9bfe7c918f98455e4/src/justhtml/treebuilder.py#L476)) unconditionally calls `_populate_selectedcontent(self.document)` at [line 494](https://github.com/EmilStenstrom/justhtml/blob/a866b6077770d9ec4cb6b6f9bfe7c918f98455e4/src/justhtml/treebuilder.py#L494). `_populate_selectedcontent()` ([`treebuilder.py#L1243`](https://github.com/EmilStenstrom/justhtml/blob/a866b6077770d9ec4cb6b6f9bfe7c918f98455e4/src/justhtml/treebuilder.py#L1243)) calls `_find_elements()` ([`treebuilder.py#L1280`](https://github.com/EmilStenstrom/justhtml/blob/a866b6077770d9ec4cb6b6f9bfe7c918f98455e4/src/justhtml/treebuilder.py#L1280)) to recursively search the DOM tree for `<select>` elements:

```python
def _find_elements(self, node: Any, name: str, result: list[Any]) -> None:
    """Recursively find all elements with given name."""
    if node.name == name:
        result.append(node)
    if node.has_child_nodes():
        for child in node.children:
            self._find_elements(child, name, result)  # recursive call
```

When the DOM tree depth exceeds CPython's default recursion limit (1000), this raises an unhandled `RecursionError`. The full call path is:

`JustHTML(html)` → `tokenizer.run()` → `tree_builder.finish()` → `_populate_selectedcontent(document)` → `_find_elements(root, "select", selects)` (recursive)

Deeply nested DOM trees can be produced by nesting `<div>` tags ~1000 levels deep. On CPython with the default recursion limit, approximately 11 KB of `<div>` nesting is sufficient to trigger the error. The exact depth threshold is environment-dependent (CPython version, recursion limit setting, call stack depth at invocation).

Additional recursive functions are affected on already-parsed deep trees:
- `Node.clone_node(deep=True)` ([`node.py#L523`](https://github.com/EmilStenstrom/justhtml/blob/a866b6077770d9ec4cb6b6f9bfe7c918f98455e4/src/justhtml/node.py#L523)) — called during sanitization
- `_node_to_html()` ([`serialize.py#L580`](https://github.com/EmilStenstrom/justhtml/blob/a866b6077770d9ec4cb6b6f9bfe7c918f98455e4/src/justhtml/serialize.py#L580)) — used by `to_html(pretty=True)`
- `_to_markdown_walk()` ([`node.py#L817`](https://github.com/EmilStenstrom/justhtml/blob/a866b6077770d9ec4cb6b6f9bfe7c918f98455e4/src/justhtml/node.py#L817)) — used by `to_markdown()`

Note: the library already uses iterative traversal in several comparable functions (e.g., `_node_to_html_compact` at [`serialize.py#L197`](https://github.com/EmilStenstrom/justhtml/blob/a866b6077770d9ec4cb6b6f9bfe7c918f98455e4/src/justhtml/serialize.py#L197), `_to_text_collect` at [`node.py#L161`](https://github.com/EmilStenstrom/justhtml/blob/a866b6077770d9ec4cb6b6f9bfe7c918f98455e4/src/justhtml/node.py#L161), `_is_blocky_element` at [`serialize.py#L405`](https://github.com/EmilStenstrom/justhtml/blob/a866b6077770d9ec4cb6b6f9bfe7c918f98455e4/src/justhtml/serialize.py#L405), `apply_to_children` at [`transforms.py#L1642`](https://github.com/EmilStenstrom/justhtml/blob/a866b6077770d9ec4cb6b6f9bfe7c918f98455e4/src/justhtml/transforms.py#L1642)), demonstrating the correct pattern.

### PoC

```python
from justhtml import JustHTML

html = "<div>" * 1000 + "x" + "</div>" * 1000
doc = JustHTML(html)  # raises RecursionError
```

Test environment: CPython 3.14.3, macOS ARM64 (Apple Silicon), justhtml 1.9.1, default recursion limit (1000)

| Input | Size | Result |
|-------|------|--------|
| `<div>` × 500 | 5,501 bytes | OK |
| `<div>` × 800 | 8,801 bytes | OK |
| `<div>` × 1000 | 11,001 bytes | RecursionError |

The error occurs with both `sanitize=True` (default) and `sanitize=False`.

### Impact

An attacker who can supply HTML for parsing can trigger an unhandled `RecursionError` during `JustHTML()` construction. The error is triggered during construction and is not avoided by `justhtml` configuration alone; mitigating it requires host-application exception handling or input constraints. Depending on the host application's exception handling, this can abort parsing, fail requests, or terminate a worker/process.

### Suggested Fix

Convert the recursive tree traversal functions to iterative implementations using an explicit stack. Example for `_find_elements`:

```python
def _find_elements(self, node: Any, name: str, result: list[Any]) -> None:
    stack = [node]
    while stack:
        current = stack.pop()
        if current.name == name:
            result.append(current)
        if current.has_child_nodes():
            stack.extend(reversed(current.children))
```

The same conversion should be applied to `_find_element`, `clone_node(deep=True)`, `_node_to_html()`, and `_to_markdown_walk()`.

## References
- https://github.com/EmilStenstrom/justhtml/security/advisories/GHSA-v7cf-c9rm-wm3j
- https://nvd.nist.gov/vuln/detail/CVE-2026-9769
- https://github.com/EmilStenstrom/justhtml
- https://github.com/EmilStenstrom/justhtml/releases/tag/v1.10.0
- https://www.vulncheck.com/advisories/justhtml-before-denial-of-service-via-deeply-nested-html
