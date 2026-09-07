# [M] Piranha CMS vulnerable to stored cross-site scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-3qcp-9v8c-6jp7
CVE: CVE-2025-61413
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-23
Source: https://github.com/advisories/GHSA-3qcp-9v8c-6jp7
Type: github-advisory

## Affected
- NuGet: `Piranha` — affected >=0

## Details
A stored cross-site scripting (XSS) vulnerability in the /manager/pages component of Piranha CMS v12.0 allows attackers to execute arbitrary web scripts or HTML via creating a page and injecting a crafted payload into the Markdown blocks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-61413
- https://github.com/PiranhaCMS/piranha.core
- https://github.com/Saconyfx/security-advisories/blob/main/CVE-2025-61413/advisory.md
- http://piranhacms.org
