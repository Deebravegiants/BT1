# [H] Thumbor proportion filter allows unbounded post-transform resize leading to remote DoS

## Summary
Severity: High
Advisory: GHSA-phj3-59pf-cp83
CVE: CVE-2026-53505
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-phj3-59pf-cp83
Type: github-advisory

## Affected
- PyPI: `thumbor` — affected >=0 <7.8.0

## Details
### Summary
Thumbor's `filters:proportion(<value>)` filter does not enforce an upper bound on `<value>` and runs in the post-transform phase. An attacker can trigger extremely large resizes (CPU/memory exhaustion) and cause denial of service.

### Details
- Filter implementation: `thumbor/filters/proportion.py`
  - `value` is parsed as a float (`BaseFilter.DecimalNumber`) with no maximum.
  - The filter computes `new_width = source_width * value` and `new_height = source_height * value` and then calls `engine.resize(new_width, new_height)`.
- Execution phase: `proportion` runs in the default POST_TRANSFORM phase (after the main transform pipeline). This means it can effectively bypass request-level size clamping that happens earlier in the request lifecycle (e.g., `MAX_WIDTH`/`MAX_HEIGHT` applied to `req.width/req.height`).

Documentation states the `percentage` argument should be `0.0 to 1.0` (`docs/proportion.rst`), but the implementation does not enforce this constraint.

### PoC
#### Preconditions
- The `proportion` filter is enabled (it is enabled by default via `BUILTIN_FILTERS`).
- Either:
  - `/unsafe/` URLs are allowed (`ALLOW_UNSAFE_URL=True`, common default in some deployments), OR
  - `/unsafe/` is disabled, and the attacker has a valid signed URL (i.e., the attacker is an authorized user/partner, or otherwise can obtain signed URLs issued by a trusted signing service).

#### Example request 1 (signed URL)
The following request was used to reproduce the issue and causes severe resource exhaustion:

`http://<host>:<port>/<url-sign>/100x100/filters:proportion(10000)/example.jpg`

#### Example request 2 (/unsafe/)
If `/unsafe/` is enabled:

`http://<host>:<port>/unsafe/100x100/filters:proportion(10000)/example.jpg`

### Impact
- Remote Denial of Service via CPU and/or memory exhaustion (and potentially process crash / OOM kill).
- Exploitability depends on deployment:
  - If `/unsafe/` is enabled: unauthenticated remote DoS.
  - If `/unsafe/` is disabled: the attacker needs a valid signed URL (i.e., the attacker can legitimately request signed URLs, or has access to signed URLs issued for other users/partners). If signed URLs are not exposed to untrusted parties, exploitability is reduced but the risk still applies to any party who can generate/use signed URLs.

### Suggested remediation
- Enforce a strict bound on the `proportion` parameter (e.g., `0.0 < value <= 1.0` as documented), or define a safe maximum based on intended semantics.

## References
- https://github.com/thumbor/thumbor/security/advisories/GHSA-phj3-59pf-cp83
- https://github.com/thumbor/thumbor/commit/2c716119de986cfc68c7071af52a98187e006023
- https://github.com/thumbor/thumbor
- https://github.com/thumbor/thumbor/releases/tag/7.8.0
