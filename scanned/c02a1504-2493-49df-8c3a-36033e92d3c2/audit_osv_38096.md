# [H] Coolify: Cross-Team IDOR via Unscoped Server and Project Lookups Exposes SSH Keys and Infrastructure

## Summary
Severity: High
Advisory: CVE-2026-34592
Aliases: GHSA-qfcc-2fm3-9q42
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-34592
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.471, Coolify server and project lookups are not scoped to the current team, allowing any authenticated user to access servers and projects belonging to other teams by specifying their IDs directly. This vulnerability is fixed in 4.0.0-beta.471.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34592.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-qfcc-2fm3-9q42
- https://nvd.nist.gov/vuln/detail/CVE-2026-34592
