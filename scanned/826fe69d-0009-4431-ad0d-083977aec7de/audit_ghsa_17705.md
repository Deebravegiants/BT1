# [M] KaTeX \htmlData does not validate attribute names

## Summary
Severity: Medium
Advisory: GHSA-cg87-wmx4-v546
CVE: CVE-2025-23207
CWE: CWE-116, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-01-17
Source: https://github.com/advisories/GHSA-cg87-wmx4-v546
Type: github-advisory

## Affected
- npm: `katex` — affected >=0.12.0 <0.16.21

## Details
### Impact
KaTeX users who render untrusted mathematical expressions with `renderToString` could encounter malicious input using `\htmlData` that runs arbitrary JavaScript, or generate invalid HTML.

### Patches
Upgrade to KaTeX v0.16.21 to remove this vulnerability.

### Workarounds
- Avoid use of or turn off the `trust` option, or set it to forbid `\htmlData` commands.
- Forbid inputs containing the substring `"\\htmlData"`.
- Sanitize HTML output from KaTeX.

### Details
`\htmlData` did not validate its attribute name argument, allowing it to generate invalid or malicious HTML that runs scripts.

### For more information
If you have any questions or comments about this advisory:

- Open an issue or security advisory in the [KaTeX repository](https://github.com/KaTeX/KaTeX/)
- Email us at [katex-security@mit.edu](mailto:katex-security@mit.edu)

## References
- https://github.com/KaTeX/KaTeX/security/advisories/GHSA-cg87-wmx4-v546
- https://nvd.nist.gov/vuln/detail/CVE-2025-23207
- https://github.com/KaTeX/KaTeX/commit/ff289955e81aab89086eef09254cbf88573d415c
- https://github.com/KaTeX/KaTeX
