# [C] CVE-2026-9558

## Summary
Severity: Critical
Advisory: CVE-2026-9558
Aliases: GHSA-9fx4-7cmj-47vg
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-9558
Type: osv

## Details
A Server-Side Template Injection (SSTI) vulnerability exists in Mautic's theme engine. The platform renders uploaded Twig templates without a sandbox or strict function restrictions. Authenticated users with permissions to create or upload themes can abuse this to execute arbitrary code on the hosting server (Remote Code Execution) or access restricted system files and configuration settings.

## References
- https://packagist.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9558.json
- https://github.com/mautic/mautic/security/advisories/GHSA-9fx4-7cmj-47vg
- https://nvd.nist.gov/vuln/detail/CVE-2026-9558
- https://github.com/mautic/mautic
