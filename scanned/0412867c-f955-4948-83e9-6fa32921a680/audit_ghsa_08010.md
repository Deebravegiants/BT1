# [M] NiceGUI vulnerable to XSS via Code Injection during client-side element function execution

## Summary
Severity: Medium
Advisory: GHSA-78qv-3mpx-9cqq
CVE: CVE-2026-27156
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-78qv-3mpx-9cqq
Type: github-advisory

## Affected
- PyPI: `nicegui` — affected >=0 <3.8.0

## Details
### Summary

Several NiceGUI APIs that execute methods on client-side elements (`Element.run_method()`, `AgGrid.run_grid_method()`, `EChart.run_chart_method()`, and others) use an `eval()` fallback in the JavaScript-side `runMethod()` function. When user-controlled input is passed as the method name, an attacker can inject arbitrary JavaScript that executes in the victim's browser.

Additionally, `Element.run_method()` and `Element.get_computed_prop()` used string interpolation instead of `json.dumps()` for the method/property name, allowing quote injection to break out of the intended string context.

### Attack Vector

An attacker crafts a malicious URL with a payload as a query parameter. If the application passes this parameter as a method name to any of the affected APIs, the payload is sent to the client via WebSocket and executed via `eval()`.

**Example:** `/?method=alert(document.cookie)` combined with application code like:
```python
element.run_method(user_provided_method_name)
```

### Impact

- Cookie/token theft
- DOM manipulation (phishing, fake login forms)
- Actions performed as the victim user

### Affected Methods

1. `Element.run_method()`
2. `Element.get_computed_prop()`
3. `AgGrid.run_grid_method()`
4. `AgGrid.run_row_method()`
5. `EChart.run_chart_method()`
6. `JsonEditor.run_editor_method()`
7. `Xterm.run_terminal_method()`
8. `Leaflet.run_map_method()`
9. `Leaflet.run_layer_method()`
10. `LeafletLayer.run_method()`

### Fix

1. Use `json.dumps()` for proper escaping of method/property names in `run_method()` and `get_computed_prop()`
2. Remove the `eval()` fallback from `runMethod()` in `nicegui.js` — method names that are not found on the element now raise an error instead of being evaluated as arbitrary JavaScript

### Migration

Code that previously passed JavaScript functions as method names needs to use `ui.run_javascript()` instead:

```python
# Before:
row = await grid.run_grid_method('g => g.getDisplayedRowAtIndex(0).data')

# After:
row = await ui.run_javascript(f'return getElement({grid.id}).api.getDisplayedRowAtIndex(0).data')
```

## References
- https://github.com/zauberzeug/nicegui/security/advisories/GHSA-78qv-3mpx-9cqq
- https://nvd.nist.gov/vuln/detail/CVE-2026-27156
- https://github.com/zauberzeug/nicegui/commit/1861f59cc374ca0dc9d970b157ef3774720f8dbf
- https://github.com/zauberzeug/nicegui
