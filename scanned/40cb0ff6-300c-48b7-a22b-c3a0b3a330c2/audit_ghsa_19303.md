# [M] Mautic's Predictable Page Indexing Might Lead to Sensitive Data Exposure

## Summary
Severity: Medium
Advisory: GHSA-cqx4-9vqf-q3m8
CVE: CVE-2025-5257
CWE: CWE-1284, CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2025-05-28
Source: https://github.com/advisories/GHSA-cqx4-9vqf-q3m8
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=4.0.0 <4.4.16
- Packagist: `mautic/core` — affected >=5.0.0-alpha <5.2.6
- Packagist: `mautic/core` — affected >=6.0.0-alpha <6.0.2

## Details
### Summary
This advisory addresses a security vulnerability in Mautic where unpublished page previews could be accessed by unauthenticated users and potentially indexed by search engines. This could lead to the unintended disclosure of draft content or sensitive information.

Unauthorized Access to Unpublished Page Previews: The page preview functionality for unpublished content, accessible via predictable URLs (e.g., `/page/preview/1`, `/page/preview/2`), lacked proper authorization checks. This allowed any unauthenticated user to view content that was not yet intended for public release, and allowed search engines to index these private preview URLs, making the content publicly discoverable.

### Mitigation
Mautic has patched this vulnerability by enforcing proper permission checks on preview pages. Users should upgrade to the patched version of Mautic or later.

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-cqx4-9vqf-q3m8
- https://nvd.nist.gov/vuln/detail/CVE-2025-5257
- https://github.com/mautic/mautic
