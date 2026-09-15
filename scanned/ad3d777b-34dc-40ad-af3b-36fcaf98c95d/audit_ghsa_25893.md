# [H] Untrusted Search Path in PNPM

## Summary
Severity: High
Advisory: GHSA-9m87-6fj3-c5xh
CVE: CVE-2022-26183
CWE: CWE-426
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-23
Source: https://github.com/advisories/GHSA-9m87-6fj3-c5xh
Type: github-advisory

## Affected
- npm: `pnpm` — affected >=0 <6.15.1

## Details
PNPM prior to v6.15.1 was discovered to contain an untrusted search path which causes the application to behave in unexpected ways when users execute PNPM commands in a directory containing malicious content. This vulnerability occurs when the application is ran on Windows OS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26183
- https://github.com/pnpm/pnpm/commit/04b7f60861ddee8331e50d70e193d1e701abeefb
- https://github.com/pnpm/pnpm
- https://github.com/pnpm/pnpm/releases/tag/v6.15.1
- https://www.sonarsource.com/blog/securing-developer-tools-package-managers
