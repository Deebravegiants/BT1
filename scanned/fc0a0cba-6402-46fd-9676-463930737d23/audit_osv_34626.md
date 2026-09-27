# [M] BookLore Media API Authentication Bypass

## Summary
Severity: Medium
Advisory: CVE-2025-62614
Aliases: GHSA-363g-fhcq-hvqp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-10-22
Source: https://osv.dev/vulnerability/CVE-2025-62614
Type: osv

## Details
BookLore is a self-hosted web app for organizing and managing personal book collections. In versions 1.8.1 and prior, an authentication bypass vulnerability in the BookMediaController allows any unauthenticated user to access and download book covers, thumbnails, and complete PDF/CBX page content without authorization. The vulnerability exists because multiple media endpoints lack proper access control annotations, and the CoverJwtFilter continues request processing even when no authentication token is provided. This enables attackers to enumerate and exfiltrate all book content from the system, bypassing the intended download permissions (canDownload) entirely. This issue has been patched via commit b226c43.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62614.json
- https://github.com/booklore-app/booklore/security/advisories/GHSA-363g-fhcq-hvqp
- https://nvd.nist.gov/vuln/detail/CVE-2025-62614
- https://github.com/booklore-app/booklore/commit/b226c43343cd0cef4c1cd54bc3dcdef90b147133
