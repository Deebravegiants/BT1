# [H] Soosyze CMS's /user/login endpoint missing rate-limiting and lockout mechanisms

## Summary
Severity: High
Advisory: GHSA-vq9x-w82r-rhmc
CVE: CVE-2025-52392
CWE: CWE-307
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-08-13
Source: https://github.com/advisories/GHSA-vq9x-w82r-rhmc
Type: github-advisory

## Affected
- Packagist: `soosyze/soosyze` — affected >=0

## Details
Soosyze CMS 2.0 allows brute-force login attacks via the /user/login endpoint due to missing rate-limiting and lockout mechanisms. An attacker can repeatedly submit login attempts without restrictions, potentially gaining unauthorized administrative access. This vulnerability corresponds to CWE-307: Improper Restriction of Excessive Authentication Attempts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-52392
- https://github.com/soosyze/soosyze/issues/269
- https://beafn28.gitbook.io/beafn28/cve/brute-force-login-vulnerability-in-soosyze-cms-2.0-cve-2025-52392
- https://github.com/soosyze/soosyze
- https://www.exploit-db.com/exploits/52416
