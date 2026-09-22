# [M] Elysia Cookie Value Prototype Pollution

## Summary
Severity: Medium
Advisory: GHSA-8hq9-phh3-p2wp
CVE: CVE-2026-31865
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-8hq9-phh3-p2wp
Type: github-advisory

## Affected
- npm: `elysia` — affected >=0 <1.4.27

## Details
### Impact
Elysia cookie can be overridden by prototype pollution , eg. `__proto__`

Sending cookie with the follows name can override cookie value:
```bash
__proto__=%7B%22injected%22%3A%22polluted%22%7D
```

### Patches
Patched by 1.4.27

### Workarounds
1. Use t.Cookie validation to enforce validation value
2. Prevent iterable over cookie if possible

## References
- https://github.com/elysiajs/elysia/security/advisories/GHSA-8hq9-phh3-p2wp
- https://nvd.nist.gov/vuln/detail/CVE-2026-31865
- https://github.com/elysiajs/elysia/commit/e9d6b1743fa7368ef942dce181f6a089757f6aab
- https://github.com/elysiajs/elysia
