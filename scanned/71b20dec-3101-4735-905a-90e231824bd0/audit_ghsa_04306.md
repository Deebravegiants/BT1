# [M] Bleach linkify(parse_email=True) CPU exhaustion via unbounded email regex scanning

## Summary
Severity: Medium
Advisory: GHSA-g75f-g53v-794x
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-g75f-g53v-794x
Type: github-advisory

## Affected
- PyPI: `bleach` — affected 6.3.0

## Details
## Summary
Bleach 6.3.0 exposes a documented email-linkification path through `bleach.linkify(..., parse_email=True)`. The implementation scans attacker-controlled text with `EMAIL_RE.finditer()` over the full character token and has no length, timeout, or linear prefilter before applying the dot-atom email regex. A non-email payload around 30 KB causes multi-second CPU consumption per request/call, creating a direct availability risk for applications that enable email linkification on user-submitted text.

## Affected Product
- Package: `bleach`
- Ecosystem: pip
- Affected versions: verified in `6.3.0`; exact first affected version not established
- Patched versions: none known at finalization time
- Tested version: `6.3.0`
- Audit commit/tag: `v6.3.0` / `5546d5dbce60d08ccb99d981778d74044d646d4e`
- PyPI sdist SHA256: `6f3b91b1c0a02bb9a78b5a454c92506aa0fdf197e1d5e114d2e00c6f64306d22`

## Vulnerability Details
- CWE: CWE-1333: Inefficient Regular Expression Complexity; related availability impact maps to CWE-400
- Component: `bleach/linkifier.py`, `build_email_re()`, `LinkifyFilter.handle_email_addresses()`
- Root cause: `handle_email_addresses()` calls `self.email_re.finditer(text)` on attacker-controlled text. `EMAIL_RE` includes a repeated dot-atom local-part pattern, so non-email strings such as repeated `a.` segments with no `@` force repeated long failing scans.
- Security boundary violated: user-submitted text processed by a documented safe linkification helper should not allow an attacker to impose superlinear CPU cost through non-email text.
- Direct impact: per-request CPU exhaustion / denial-of-service risk in applications that enable `parse_email=True` on attacker-controlled text.
- Chain impact, if any: one proof run observed an unrelated `/health` request delayed during a concurrent attack request, but this was not reliable across reviewer retests. Treat cross-request service degradation as environment-dependent supporting evidence, not the primary impact.
- Severity estimate: Medium / availability-only. The feature is opt-in and deployment body limits/timeouts affect practical severity.

Relevant code path:
- `bleach/__init__.py:85-125`: public `linkify(text, ..., parse_email=False)` constructs `Linker(..., parse_email=parse_email)` and calls `linker.linkify(text)`.
- `bleach/linkifier.py:77-88`: `EMAIL_RE` is compiled from the dot-atom email pattern.
- `bleach/linkifier.py:292-301`: `handle_email_addresses()` applies `self.email_re.finditer(text)` to each character token.
- `bleach/linkifier.py:620-623`: character tokens are routed into email handling only when `parse_email` is true.
- `docs/goals.rst:30-40`: Bleach documents user comments, profile bios, and descriptions as target untrusted text use cases.
- `docs/linkify.rst:300-305`: `parse_email=True` is the documented option for creating `mailto:` links.

## Attack Preconditions
- The consuming application enables the documented `parse_email=True` option, for example `bleach.linkify(user_text, parse_email=True)` or `Linker(parse_email=True).linkify(user_text)`.
- The attacker can submit text that reaches that linkification path. Authentication depends on the host application; a public comment form would make this unauthenticated, while account-only text fields require user privileges.
- The application allows roughly 20-30 KB of text to reach Bleach and lacks a strict timeout or input cap before linkification.
- No custom bounded `email_re` is supplied.

## Reproduction
Minimal API trigger:

```python
import bleach
payload = ("a." * 15000) + "a"
bleach.linkify(payload, parse_email=True)
```

The saved HTTP proof uses a local harness with `POST /preview` calling `bleach.linkify(request_body, parse_email=True)` and a control endpoint using `parse_email=False` on the same payload. The exploit sends baseline/control/attack requests over HTTP to `127.0.0.1`.

## Proof Evidence
The proof ran against Bleach `6.3.0` installed from the audited local checkout in an isolated temporary venv. It used Python `3.12.3` on Linux.

Measured HTTP proof results:
- Payload: `("a." * 15000) + "a"` (`30001` bytes)
- Normal baseline `/preview` mean: `0.001425` seconds
- Same 30 KB payload with `parse_email=False`: `0.048349` seconds
- Attack payload with `parse_email=True`: `8.719818` seconds
- Slowdown versus the larger baseline/control mean: `180.35x`
- Requests sent by proof: `20`

Evidence files:
[poc.py](https://github.com/user-attachments/files/27129729/poc.py)
[poc_results.json](https://github.com/user-attachments/files/27129737/poc_results.json)
[exploit_proof.py](https://github.com/user-attachments/files/27129751/exploit_proof.py)
[exploit_results.json](https://github.com/user-attachments/files/27129752/exploit_results.json)

## Scope and Limitations
- This report does not claim XSS, authentication bypass, data disclosure, remote code execution, persistent crash, or persistent service outage.
- `parse_email=True` is not the default. The affected path is a documented opt-in feature.
- The exact first affected version is not established.
- Practical impact depends on host application input limits, worker model, request timeout policy, and whether untrusted users can submit text to an email-linkification path.
- A reviewer reproduced the direct CPU cost but did not reproduce the proof harness’s `/health` delay. The direct impact claim is therefore limited to per-request CPU exhaustion.
- Bleach is marked deprecated in `README.rst`, and `SECURITY.md` has stale supported-version text, but the package still has a 2025 PyPI release and published Mozilla security reporting routes.

## References
- https://github.com/mozilla/bleach/security/advisories/GHSA-g75f-g53v-794x
- https://github.com/mozilla/bleach
