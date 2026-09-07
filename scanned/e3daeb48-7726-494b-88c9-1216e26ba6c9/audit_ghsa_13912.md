# [M] Mind-elixir Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-m22q-97p5-79v2
CVE: CVE-2021-32851
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-21
Source: https://github.com/advisories/GHSA-m22q-97p5-79v2
Type: github-advisory

## Affected
- npm: `mind-elixir` — affected >=0 <0.18.1

## Details
Mind-elixir is a free, open source mind map core. Prior to version 0.18.1, mind-elixir is prone to cross-site scripting when handling untrusted menus. This issue is patched in version 0.18.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32851
- https://github.com/ssshooter/mind-elixir-core/commit/073485269ac83af24371f35bd08507defa885655
- https://github.com/ssshooter/mind-elixir-core
- https://github.com/ssshooter/mind-elixir-core/blob/79942a68b14c8875ab7d270b1ad25bfff351b04c/src/plugin/contextMenu.js#L13
- https://securitylab.github.com/advisories/GHSL-2021-1047_Mind-elixir
