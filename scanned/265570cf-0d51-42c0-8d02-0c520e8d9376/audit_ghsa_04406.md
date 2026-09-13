# [C] shell-quote quote() does not escape newlines in object .op values

## Summary
Severity: Critical
Advisory: GHSA-w7jw-789q-3m8p
CVE: CVE-2026-9277
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-w7jw-789q-3m8p
Type: github-advisory

## Affected
- npm: `shell-quote` — affected >=1.1.0 <1.8.4

## Details
### Summary

`shell-quote`'s `quote()` function did not validate object-token inputs against the operator model used by `parse()`. The `.op` field was backslash-escaped character by character using `/(.)/g`, which in JavaScript does not match line terminators (`\n`, `\r`, U+2028, U+2029). A line terminator in `.op` therefore passed through unescaped into the output; POSIX shells treat a literal `\n` as a command separator, so any content after it would execute as a second command.

The vulnerable code path is reachable in two ways. Neither requires the parser to misbehave — `parse()` only emits ops from a fixed control set — but both are documented API surface:

1. **Direct construction.** A caller builds `{ op: '...\n...' }` from external input (e.g. a deserialized argument array) and passes it to `quote()`.
2. **`envFn` return.** `parse(cmd, envFn)` is documented to splice the return value of `envFn` into the result array when it is an object. An attacker-influenced data source consulted by `envFn` can introduce an object token whose `.op` reaches `quote()`.

### Impact

Shell command injection in callers that pass object tokens with attacker-influenced `.op` values to `quote()` and then hand the result to a shell. The preconditions are narrower than ordinary string injection — they require the caller to feed object tokens into `quote()` — but object tokens are a public, documented part of the API surface, and `quote()` is intended to be a shell-safety boundary.

### PoC

```js
const { parse, quote } = require('shell-quote');

// Direct construction
quote([{ op: ';\nid' }]);
// → "\;\n\\i\\d"  ← literal newline; second line executes as a command

// Via parse() with an envFn returning attacker-shaped objects
const tokens = parse('echo $X', () => ({ op: ';\nid' }));
require('child_process').execSync(quote(tokens), { shell: true });
// Executes `id` after `echo \;`.
```

Confirmed under `sh`, `bash`, `dash`, and `zsh`.

### Patch

Fixed by replacing the per-character escape with strict shape validation in `quote()`. The object-token branch now:

- **`{ op }`** — `.op` must be a string from the same allowlist the parser emits (`||`, `&&`, `;;`, `|&`, `<(`, `<<<`, `>>`, `>&`, `<&`, `&`, `;`, `(`, `)`, `|`, `<`, `>`). Anything else throws `TypeError`. This is the direct fix for the reported issue and removes the entire class of `.op` injection.
- **`{ op: 'glob', pattern }`** — `.pattern` must be a string with no line terminators. Glob metacharacters (`*`, `?`, `[`, `]`, `{`, `}`, `,`) pass through; all other shell-special characters are backslash-escaped. (Previously the pattern field was discarded entirely and the literal string `\g\l\o\b` was emitted — a latent bug, not security-relevant.)
- **`{ comment }`** — `.comment` must be a string with no line terminators (line terminators would end the shell comment and resume command parsing — same injection shape).
- **Any other object shape** — `TypeError`.

The fix is allowlist-based rather than a targeted regex tweak, so it closes the reported vector and forecloses adjacent ones (U+2028 / U+2029 line separators in `.op`, line terminators in comments, unknown-shape objects coerced through `.replace`).

### Workarounds

Prior to upgrading, callers that build object tokens from untrusted input should validate `.op` against the parser's operator set themselves, and never construct `{ op }` from attacker-controlled strings.

### Credits

Reported by Akshat Sinha

## References
- https://github.com/ljharb/shell-quote/security/advisories/GHSA-w7jw-789q-3m8p
- https://nvd.nist.gov/vuln/detail/CVE-2026-9277
- https://github.com/ljharb/shell-quote/commit/1518179
- https://github.com/ljharb/shell-quote
- https://www.npmjs.com/package/shell-quote
- http://www.openwall.com/lists/oss-security/2026/05/23/2
