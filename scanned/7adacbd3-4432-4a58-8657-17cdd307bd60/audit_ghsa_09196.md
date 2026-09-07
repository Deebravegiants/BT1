# [M] ip-address has XSS in Address6 HTML-emitting methods

## Summary
Severity: Medium
Advisory: GHSA-v2v4-37r5-5v8g
CVE: CVE-2026-42338
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-v2v4-37r5-5v8g
Type: github-advisory

## Affected
- npm: `ip-address` — affected >=0 <10.1.1

## Details
### Summary

`Address6.group()` and `Address6.link()` do not HTML-escape attacker-controlled content before embedding it in the HTML strings they return, and `AddressError.parseMessage` (emitted by the `Address6` constructor for invalid input) can contain unescaped attacker-controlled content in one branch. An application that (1) passes untrusted input to `Address6` and (2) renders the output of these methods, or the thrown error's `parseMessage`, as HTML (e.g. via `innerHTML`) is vulnerable to cross-site scripting. A related issue in `v6.helpers.spanAll()` produced malformed markup but was not exploitable; it is hardened in the same release for consistency.

### Details

Four related issues were identified and fixed together:

1. **`Address6.group()`: zone ID injection.** The `Address6` constructor stores the raw input (including any IPv6 zone ID) in `this.address` before zone stripping. `group()` then passed `this.address` to `helpers.simpleGroup()`, which wrapped each `:`-separated segment in a `<span>` element without HTML-escaping the content. A zone ID containing HTML markup was embedded verbatim.
2. **`Address6.link({ prefix, className })`: attribute-value injection.** `link()` concatenated user-supplied `prefix` and `className` into the `href="…"` and `class="…"` attributes without escaping. A caller passing untrusted content through these options could inject event handlers (e.g. `onmouseover`) and achieve XSS.
3. **`Address6` constructor: leading-zero IPv4 error path.** The leading-zero branch in `parse4in6()` built `AddressError.parseMessage` by concatenating the raw address through `String.replace()`. Because `parse4in6()` runs before the bad-character check, any characters in the groups preceding the IPv4 suffix flowed into the error's HTML unescaped. Consumers who render `parseMessage` as HTML (its documented purpose — it already contains `<span class="parse-error">` markup) could be XSS'd by a crafted input such as `<img src=x onerror=alert(1)>:10.0.01.1`.
4. **`v6.helpers.spanAll()`: attribute-value injection (defense in depth).** `spanAll()` embedded each character of its input into a `class="digit value-${n} …"` attribute without escaping. Because `split('')` limits `n` to a single character this was not exploitable in practice, but it produced malformed markup and is fixed for consistency.

### Affected Versions

All versions up to and including `10.1.0`.

### Patched Version

`10.1.1`.

### Impact

Real-world exposure is believed to be extremely limited. Analysis of all 425 dependent npm packages as well as GitHub code search found zero consumers of `group()`, `link()`, or `spanAll()`: these HTML-emitting surfaces appear to be unused across published npm packages and public repositories. Applications using only the address-parsing and comparison APIs (`isValid`, `correctForm`, `isInSubnet`, `bigInt`, etc.) are not affected.

Consumers who **do** render the output of `group()`, `link()`, `spanAll()`, or `AddressError.parseMessage` as HTML against untrusted input should upgrade.

### PoC

```javascript
const { Address6 } = require('ip-address');
const addr = new Address6('fe80::1%<img src=x onerror=alert(1)>');
document.body.innerHTML = addr.group();  // fires the onerror handler in 10.1.0
```

### Workarounds

If users cannot upgrade immediately:

- Do not pass untrusted input to the `Address6` constructor, or
- Never render the output of `group()`, `link()`, or `spanAll()`, nor the `parseMessage` field of any thrown `AddressError`, as HTML; treat these values as text only, or run them through [DOMPurify](https://github.com/cure53/DOMPurify) before inserting into the DOM (DOMPurify's default configuration preserves the library's intended `<span>` wrapping while stripping any injected event handlers), or
- Validate input with `Address6.isValid()` and reject anything that contains a zone identifier (a `%` character) or characters outside `[0-9a-fA-F:/]` before passing it to the constructor.

### Lack of separate CVEs

Given the evidence that these methods are not used, and given that they are all of the same construction, maintainers do not think it's relevant or useful to create a separate CVE for each library method.

### Credit

ip-address thanks @scovetta for reporting this issue.

## References
- https://github.com/beaugunderson/ip-address/security/advisories/GHSA-v2v4-37r5-5v8g
- https://nvd.nist.gov/vuln/detail/CVE-2026-42338
- https://github.com/beaugunderson/ip-address
