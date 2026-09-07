# [M] Cross-site Scripting in PiranhaCMS

## Summary
Severity: Medium
Advisory: GHSA-jvjp-vh27-r9h5
CVE: CVE-2021-25977
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-10-27
Source: https://github.com/advisories/GHSA-jvjp-vh27-r9h5
Type: github-advisory

## Affected
- NuGet: `Piranha` — affected >=7.0.0 <9.2.0

## Details
In PiranhaCMS, versions 7.0.0 to 9.1.1 are vulnerable to stored XSS due to the page title improperly sanitized. By creating a page with a specially crafted page title, a low privileged user can trigger arbitrary JavaScript execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25977
- https://github.com/PiranhaCMS/piranha.core/commit/543bc53c7dbd28c793ec960b57fb0e716c6b18d7
- https://github.com/PiranhaCMS/piranha.core
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25977
