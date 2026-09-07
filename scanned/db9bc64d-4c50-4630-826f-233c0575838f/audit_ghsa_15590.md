# [H] path-to-regexp outputs backtracking regular expressions

## Summary
Severity: High
Advisory: GHSA-9wv6-86v2-598j
CVE: CVE-2024-45296
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-09-09
Source: https://github.com/advisories/GHSA-9wv6-86v2-598j
Type: github-advisory

## Affected
- npm: `path-to-regexp` — affected >=0.2.0 <1.9.0
- npm: `path-to-regexp` — affected >=0 <0.1.10
- npm: `path-to-regexp` — affected >=7.0.0 <8.0.0
- npm: `path-to-regexp` — affected >=2.0.0 <3.3.0
- npm: `path-to-regexp` — affected >=4.0.0 <6.3.0

## Details
### Impact

A bad regular expression is generated any time you have two parameters within a single segment, separated by something that is not a period (`.`). For example, `/:a-:b`.

### Patches

For users of 0.1, upgrade to `0.1.10`. All other users should upgrade to `8.0.0`.

These versions add backtrack protection when a custom regex pattern is not provided:

- [0.1.10](https://github.com/pillarjs/path-to-regexp/releases/tag/v0.1.10)
- [1.9.0](https://github.com/pillarjs/path-to-regexp/releases/tag/v1.9.0)
- [3.3.0](https://github.com/pillarjs/path-to-regexp/releases/tag/v3.3.0)
- [6.3.0](https://github.com/pillarjs/path-to-regexp/releases/tag/v6.3.0)

They do not protect against vulnerable user supplied capture groups. Protecting against explicit user patterns is out of scope for old versions and not considered a vulnerability.

Version [7.1.0](https://github.com/pillarjs/path-to-regexp/releases/tag/v7.1.0) can enable `strict: true` and get an error when the regular expression might be bad.

Version [8.0.0](https://github.com/pillarjs/path-to-regexp/releases/tag/v8.0.0) removes the features that can cause a ReDoS.

### Workarounds

All versions can be patched by providing a custom regular expression for parameters after the first in a single segment. As long as the custom regular expression does not match the text before the parameter, you will be safe. For example, change `/:a-:b` to `/:a-:b([^-/]+)`.

If paths cannot be rewritten and versions cannot be upgraded, another alternative is to limit the URL length. For example, halving the attack string improves performance by 4x faster.

### Details

Using `/:a-:b` will produce the regular expression `/^\/([^\/]+?)-([^\/]+?)\/?$/`. This can be exploited by a path such as `/a${'-a'.repeat(8_000)}/a`. [OWASP](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS) has a good example of why this occurs, but the TL;DR is the `/a` at the end ensures this route would never match but due to naive backtracking it will still attempt every combination of the `:a-:b` on the repeated 8,000 `-a`.

Because JavaScript is single threaded and regex matching runs on the main thread, poor performance will block the event loop and can lead to a DoS. In local benchmarks, exploiting the unsafe regex will result in performance that is over 1000x worse than the safe regex. In a more realistic environment using Express v4 and 10 concurrent connections, this translated to average latency of ~600ms vs 1ms.

### References

* [OWASP](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)
* [Detailed blog post](https://blakeembrey.com/posts/2024-09-web-redos/)

## References
- https://github.com/pillarjs/path-to-regexp/security/advisories/GHSA-9wv6-86v2-598j
- https://nvd.nist.gov/vuln/detail/CVE-2024-45296
- https://github.com/pillarjs/path-to-regexp/commit/29b96b4a1de52824e1ca0f49a701183cc4ed476f
- https://github.com/pillarjs/path-to-regexp/commit/60f2121e9b66b7b622cc01080df0aabda9eedee6
- https://github.com/pillarjs/path-to-regexp/commit/925ac8e3c5780b02f58cbd4e52f95da8ad2ac485
- https://github.com/pillarjs/path-to-regexp/commit/d31670ae8f6e69cbfd56e835742195b7d10942ef
- https://github.com/pillarjs/path-to-regexp/commit/f1253b47b347dcb909e3e80b0eb2649109e59894
- https://github.com/pillarjs/path-to-regexp
- https://github.com/pillarjs/path-to-regexp/releases/tag/v6.3.0
- https://security.netapp.com/advisory/ntap-20250124-0001
