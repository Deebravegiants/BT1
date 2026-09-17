# [H] minimatch has a ReDoS via repeated wildcards with non-matching literal in pattern

## Summary
Severity: High
Advisory: GHSA-3ppc-4f35-3m26
CVE: CVE-2026-26996
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-3ppc-4f35-3m26
Type: github-advisory

## Affected
- npm: `minimatch` — affected >=10.0.0 <10.2.1
- npm: `minimatch` — affected >=9.0.0 <9.0.6
- npm: `minimatch` — affected >=8.0.0 <8.0.5
- npm: `minimatch` — affected >=7.0.0 <7.4.7
- npm: `minimatch` — affected >=6.0.0 <6.2.1
- npm: `minimatch` — affected >=5.0.0 <5.1.7
- npm: `minimatch` — affected >=4.0.0 <4.2.4
- npm: `minimatch` — affected >=0 <3.1.3

## Details
### Summary
`minimatch` is vulnerable to Regular Expression Denial of Service (ReDoS) when a glob pattern contains many consecutive `*` wildcards followed by a literal character that doesn't appear in the test string. Each `*` compiles to a separate `[^/]*?` regex group, and when the match fails, V8's regex engine backtracks exponentially across all possible splits.

The time complexity is O(4^N) where N is the number of `*` characters. With N=15, a single `minimatch()` call takes ~2 seconds. With N=34, it hangs effectively forever.


### Details
_Give all details on the vulnerability. Pointing to the incriminated source code is very helpful for the maintainer._

### PoC
When minimatch compiles a glob pattern, each `*` becomes `[^/]*?` in the generated regex. For a pattern like `***************X***`:

```
/^(?!\.)[^/]*?[^/]*?[^/]*?[^/]*?[^/]*?[^/]*?[^/]*?[^/]*?[^/]*?[^/]*?[^/]*?[^/]*?[^/]*?[^/]*?[^/]*?X[^/]*?[^/]*?[^/]*?$/
```

When the test string doesn't contain `X`, the regex engine must try every possible way to distribute the characters across all the `[^/]*?` groups before concluding no match exists. With N groups and M characters, this is O(C(N+M, N)) — exponential.
### Impact
Any application that passes user-controlled strings to `minimatch()` as the pattern argument is vulnerable to DoS. This includes:
- File search/filter UIs that accept glob patterns
- `.gitignore`-style filtering with user-defined rules
- Build tools that accept glob configuration
- Any API that exposes glob matching to untrusted input

----

Thanks to @ljharb for back-porting the fix to legacy versions of minimatch.

## References
- https://github.com/isaacs/minimatch/security/advisories/GHSA-3ppc-4f35-3m26
- https://nvd.nist.gov/vuln/detail/CVE-2026-26996
- https://github.com/isaacs/minimatch/commit/2e111f3a79abc00fa73110195de2c0f2351904f5
- https://github.com/isaacs/minimatch
