# [H] Picomatch has a ReDoS vulnerability via extglob quantifiers

## Summary
Severity: High
Advisory: GHSA-c2c7-rcm5-vvqj
CVE: CVE-2026-33671
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-c2c7-rcm5-vvqj
Type: github-advisory

## Affected
- npm: `picomatch` — affected >=4.0.0 <4.0.4
- npm: `picomatch` — affected >=3.0.0 <3.0.2
- npm: `picomatch` — affected >=0 <2.3.2

## Details
### Impact
`picomatch` is vulnerable to Regular Expression Denial of Service (ReDoS) when processing crafted extglob patterns. Certain patterns using extglob quantifiers such as `+()` and `*()`, especially when combined with overlapping alternatives or nested extglobs, are compiled into regular expressions that can exhibit catastrophic backtracking on non-matching input.

Examples of problematic patterns include `+(a|aa)`, `+(*|?)`, `+(+(a))`, `*(+(a))`, and `+(+(+(a)))`. In local reproduction, these patterns caused multi-second event-loop blocking with relatively short inputs. For example, `+(a|aa)` compiled to `^(?:(?=.)(?:a|aa)+)$` and took about 2 seconds to reject a 41-character non-matching input, while nested patterns such as `+(+(a))` and `*(+(a))` took around 29 seconds to reject a 33-character input on a modern M1 MacBook.

Applications are impacted when they allow untrusted users to supply glob patterns that are passed to `picomatch` for compilation or matching. In those cases, an attacker can cause excessive CPU consumption and block the Node.js event loop, resulting in a denial of service. Applications that only use trusted, developer-controlled glob patterns are much less likely to be exposed in a security-relevant way.

### Patches
This issue is fixed in picomatch 4.0.4, 3.0.2 and 2.3.2.

Users should upgrade to one of these versions or later, depending on their supported release line.

### Workarounds
If upgrading is not immediately possible, avoid passing untrusted glob patterns to `picomatch`.

Possible mitigations include:
- disable extglob support for untrusted patterns by using `noextglob: true`
- reject or sanitize patterns containing nested extglobs or extglob quantifiers such as `+()` and `*()`
- enforce strict allowlists for accepted pattern syntax
- run matching in an isolated worker or separate process with time and resource limits
- apply application-level request throttling and input validation for any endpoint that accepts glob patterns

### Resources
- Picomatch repository: https://github.com/micromatch/picomatch
- `lib/parse.js` and `lib/constants.js` are involved in generating the vulnerable regex forms
- Comparable ReDoS precedent: CVE-2024-4067 (`micromatch`)
- Comparable generated-regex precedent: CVE-2024-45296 (`path-to-regexp`)

## References
- https://github.com/micromatch/picomatch/security/advisories/GHSA-c2c7-rcm5-vvqj
- https://nvd.nist.gov/vuln/detail/CVE-2026-33671
- https://github.com/micromatch/picomatch/commit/5eceecd27543b8e056b9307d69e105ea03618a7d
- https://github.com/micromatch/picomatch
