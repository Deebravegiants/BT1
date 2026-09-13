# [M] KaTeX's maxExpand bypassed by Unicode sub/superscripts

## Summary
Severity: Medium
Advisory: GHSA-cvr6-37gx-v8wc
CVE: CVE-2024-28244
CWE: CWE-606, CWE-674
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-25
Source: https://github.com/advisories/GHSA-cvr6-37gx-v8wc
Type: github-advisory

## Affected
- npm: `katex` — affected >=0.15.4 <0.16.10

## Details
### Impact
KaTeX users who render untrusted mathematical expressions could encounter malicious input using `\def` or `\newcommand` that causes a near-infinite loop, despite setting `maxExpand` to avoid such loops. This can be used as an availability attack, where e.g. a client rendering another user's KaTeX input will be unable to use the site due to memory overflow, tying up the main thread, or stack overflow.

### Patches
Upgrade to KaTeX v0.16.10 to remove this vulnerability.

### Workarounds
Forbid inputs containing any of the characters `₊₋₌₍₎₀₁₂₃₄₅₆₇₈₉ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓᵦᵧᵨᵩᵪ⁺⁻⁼⁽⁾⁰¹²³⁴⁵⁶⁷⁸⁹ᵃᵇᶜᵈᵉᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘʷˣʸᶻᵛᵝᵞᵟᵠᵡ` before passing them to KaTeX.
(There is no easy workaround for the auto-render extension.)

### Details
KaTeX supports an option named `maxExpand` which aims to prevent infinitely recursive macros from consuming all available memory and/or triggering a stack overflow error. Unfortunately, [support for "Unicode (sub|super)script characters"](https://github.com/KaTeX/KaTeX/commit/d8fc35e6a97f8e561c723b93ad275cf5a7f3094a) allows an attacker to bypass this limit. Each sub/superscript group instantiated a separate Parser with its own limit on macro executions, without inheriting the current count of macro executions from its parent. This has been corrected in KaTeX v0.16.10.

### For more information
If you have any questions or comments about this advisory:
* Open an issue or security advisory in the [KaTeX repository](https://github.com/KaTeX/KaTeX/)
* Email us at [katex-security@mit.edu](mailto:katex-security@mit.edu)

## References
- https://github.com/KaTeX/KaTeX/security/advisories/GHSA-cvr6-37gx-v8wc
- https://nvd.nist.gov/vuln/detail/CVE-2024-28244
- https://github.com/KaTeX/KaTeX/commit/085e21b5da05414efefa932570e7201a7c70e5b2
- https://github.com/KaTeX/KaTeX
