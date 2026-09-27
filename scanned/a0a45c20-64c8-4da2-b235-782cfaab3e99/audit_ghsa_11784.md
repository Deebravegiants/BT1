# [M] yaml is vulnerable to Stack Overflow via deeply nested YAML collections

## Summary
Severity: Medium
Advisory: GHSA-48c2-rrv3-qjmp
CVE: CVE-2026-33532
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-48c2-rrv3-qjmp
Type: github-advisory

## Affected
- npm: `yaml` — affected >=2.0.0 <2.8.3
- npm: `yaml` — affected >=1.0.0 <1.10.3

## Details
Parsing a YAML document with `yaml` may throw a RangeError due to a stack overflow.

The node resolution/composition phase uses recursive function calls without a depth bound. An attacker who can supply YAML for parsing can trigger a `RangeError: Maximum call stack size exceeded` with a small payload (~2–10 KB). The `RangeError` is not a `YAMLParseError`, so applications that only catch YAML-specific errors will encounter an unexpected exception type. Depending on the host application's exception handling, this can fail requests or terminate the Node.js process.

Flow sequences allow deep nesting with minimal bytes (2 bytes per level: one `[` and one `]`). On the default Node.js stack, approximately 1,000–5,000 levels of nesting (2–10 KB input) exhaust the call stack. The exact threshold is environment-dependent (Node.js version, stack size, call stack depth at invocation).

Note: the library's `Parser` (CST phase) uses a stack-based iterative approach and is not affected. Only the compose/resolve phase uses actual call-stack recursion.

All three public parsing APIs are affected: `YAML.parse()`, `YAML.parseDocument()`, and `YAML.parseAllDocuments()`.

### PoC

```javascript
const YAML = require('yaml');

// ~10 KB payload: 5000 levels of nested flow sequences
const payload = '['.repeat(5000) + '1' + ']'.repeat(5000);

try {
  YAML.parse(payload);
} catch (e) {
  console.log(e.constructor.name); // RangeError (NOT YAMLParseError)
  console.log(e.message);          // Maximum call stack size exceeded
}
```

Test environment: Node.js v24.12.0, macOS darwin arm64

| Version | Nesting Depth | Input Size | Result |
|---|---|---|---|
| 1.0.0 | 5,000 | 10,001 B | RangeError |
| 1.10.2 | 5,000 | 10,001 B | RangeError |
| 2.0.0 | 5,000 | 10,001 B | RangeError |
| 2.8.2 | 5,000 | 10,001 B | RangeError |
| 2.8.3 | 5,000 | 10,001 B | YAMLParseError |

Depth threshold on yaml 2.8.2:

| Nesting Depth | Input Size | Result |
|---|---|---|
| 500 | 1,001 B | Parses successfully |
| 1,000 | 2,001 B | RangeError (threshold varies by stack size) |
| 5,000 | 10,001 B | RangeError |

## References
- https://github.com/eemeli/yaml/security/advisories/GHSA-48c2-rrv3-qjmp
- https://nvd.nist.gov/vuln/detail/CVE-2026-33532
- https://github.com/eemeli/yaml/commit/1e84ebbea7ec35011a4c61bbb820a529ee4f359b
- https://github.com/eemeli/yaml
- https://github.com/eemeli/yaml/releases/tag/v1.10.3
- https://github.com/eemeli/yaml/releases/tag/v2.8.3
