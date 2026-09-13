# [M] KaTeX's `\includegraphics` does not escape filename

## Summary
Severity: Medium
Advisory: GHSA-f98w-7cxr-ff2h
CVE: CVE-2024-28245
CWE: CWE-116
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-03-25
Source: https://github.com/advisories/GHSA-f98w-7cxr-ff2h
Type: github-advisory

## Affected
- npm: `katex` — affected >=0.11.0 <0.16.10

## Details
### Impact
KaTeX users who render untrusted mathematical expressions could encounter malicious input using `\includegraphics` that runs arbitrary JavaScript, or generate invalid HTML.

### Patches
Upgrade to KaTeX v0.16.10 to remove this vulnerability.

### Workarounds
* Avoid use of or turn off the `trust` option, or set it to forbid `\includegraphics` commands.
* Forbid inputs containing the substring `"\\includegraphics"`.
* Sanitize HTML output from KaTeX.

### Details
`\includegraphics` did not properly quote its filename argument, allowing it to generate invalid or malicious HTML that runs scripts.

### For more information
If you have any questions or comments about this advisory:

* Open an issue or security advisory in the [KaTeX repository](https://github.com/KaTeX/KaTeX/)
* Email us at katex-security@mit.edu

## References
- https://github.com/KaTeX/KaTeX/security/advisories/GHSA-f98w-7cxr-ff2h
- https://nvd.nist.gov/vuln/detail/CVE-2024-28245
- https://github.com/KaTeX/KaTeX/commit/c5897fcd1f73da9612a53e6b5544f1d776e17770
- https://github.com/KaTeX/KaTeX
