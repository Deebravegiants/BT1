# [H] Server-Side Request Forgery in scout-browser

## Summary
Severity: High
Advisory: GHSA-g53g-q539-93cv
CVE: CVE-2022-1592
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-06
Source: https://github.com/advisories/GHSA-g53g-q539-93cv
Type: github-advisory

## Affected
- PyPI: `scout-browser` — affected >=0 <4.52

## Details
Pypi package scout-browser (GitHub repository clinical-genomics/scout) prior to v4.52 is vulnerable to server-side request forgery. An attacker could make the application perform arbitrary requests to steal cookies, request access to private areas, or lead to cross-site scripting.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1592
- https://github.com/Clinical-Genomics/scout/issues/3325
- https://github.com/Clinical-Genomics/scout/pull/3326
- https://github.com/clinical-genomics/scout/commit/b0ef15f4737d0c801154c1991b52ff5cab4f5c83
- https://github.com/clinical-genomics/scout
- https://huntr.dev/bounties/352b39da-0f2e-415a-9793-5480cae8bd27
