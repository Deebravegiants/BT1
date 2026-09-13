# [H] Unauthenticated file upload via missing authorization on formatter upload endpoint

## Summary
Severity: High
Advisory: CVE-2026-63219
Aliases: GHSA-mh22-prqr-vf42
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-63219
Type: osv

## Details
GeoNetwork is a catalog application to manage spatially referenced resources. Prior to versions 4.4.12 and 4.2.17, the API endpoint for creating a new formatter via file upload is unprotected and allows the upload of external uncontrolled files. An unauthenticated attacker can upload arbitrary `.xsl` or `.zip` formatter files to the server.  An unauthenticated attacker can write arbitrary files into the GeoNetwork formatter directory. On its own this constitutes unauthorized write access to server storage. The issue is patched in GeoNetwork versions 4.4.12 and 4.2.17.

## References
- https://docs.geonetwork-opensource.org/4.2/overview/change-log/version-4.2.17
- https://docs.geonetwork-opensource.org/4.4/overview/change-log/version-4.4.12
- https://thehackernews.com/2026/09/geonetwork-fixes-unauthenticated-rce.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63219.json
- https://github.com/geonetwork/core-geonetwork/security/advisories/GHSA-mh22-prqr-vf42
- https://nvd.nist.gov/vuln/detail/CVE-2026-63219
- https://github.com/geonetwork/core-geonetwork/pull/9346
