# [H] next-mdx-remote affected by arbitrary code execution in React server-side rendering of untrusted MDX content

## Summary
Severity: High
Advisory: GHSA-g4xw-jxrg-5f6m
CVE: CVE-2026-0969
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-12
Source: https://github.com/advisories/GHSA-g4xw-jxrg-5f6m
Type: github-advisory

## Affected
- npm: `next-mdx-remote` — affected >=4.3.0 <6.0.0

## Details
The serialize function used to compile MDX in next-mdx-remote is vulnerable to arbitrary code execution due to insufficient sanitization of MDX content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-0969
- https://github.com/hashicorp/next-mdx-remote/commit/4d527fdcaed911b87f427d0b4d3c711e817fa4b3
- https://discuss.hashicorp.com/t/hcsec-2026-01-arbitrary-code-execution-in-react-server-side-rendering-of-untrusted-mdx-content/77155
- https://github.com/hashicorp/next-mdx-remote
- https://github.com/hashicorp/next-mdx-remote/releases/tag/v6.0.0
