# [M] KaTeX's maxExpand bypassed by `\edef`

## Summary
Severity: Medium
Advisory: GHSA-64fm-8hw2-v72w
CVE: CVE-2024-28243
CWE: CWE-606, CWE-674
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-25
Source: https://github.com/advisories/GHSA-64fm-8hw2-v72w
Type: github-advisory

## Affected
- npm: `katex` — affected >=0.12.0 <0.16.10

## Details
### Impact
KaTeX users who render untrusted mathematical expressions could encounter malicious input using `\edef` that causes a near-infinite loop, despite setting `maxExpand` to avoid such loops. This can be used as an availability attack, where e.g. a client rendering another user's KaTeX input will be unable to use the site due to memory overflow, tying up the main thread, or stack overflow.

### Patches
Upgrade to KaTeX v0.16.10 to remove this vulnerability.

### Workarounds
Forbid inputs containing the substring `"\\edef"` before passing them to KaTeX.
(There is no easy workaround for the auto-render extension.)

### Details
KaTeX supports an option named `maxExpand` which prevents infinitely recursive macros from consuming all available memory and/or triggering a stack overflow error. However, what counted as an "expansion" is a single macro expanding to any number of tokens. The expand-and-define TeX command `\edef` can be used to build up an exponential number of tokens using only a linear number of expansions according to this definition, e.g. by repeatedly doubling the previous definition. This has been corrected in KaTeX v0.16.10, where every expanded token in an `\edef` counts as an expansion.

### For more information
If you have any questions or comments about this advisory:
* Open an issue or security advisory in the [KaTeX repository](https://github.com/KaTeX/KaTeX/)
* Email us at [katex-security@mit.edu](mailto:katex-security@mit.edu)

## References
- https://github.com/KaTeX/KaTeX/security/advisories/GHSA-64fm-8hw2-v72w
- https://nvd.nist.gov/vuln/detail/CVE-2024-28243
- https://github.com/github/advisory-database/pull/6777
- https://github.com/KaTeX/KaTeX/commit/e88b4c357f978b1bca8edfe3297f0aa309bcbe34
- https://github.com/KaTeX/KaTeX
