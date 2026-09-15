# [C] Simofa Allows Unauthenticated Access to API Routes

## Summary
Severity: Critical
Advisory: CVE-2024-56799
Aliases: GHSA-83qw-5qq5-v7pq
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2024-12-30
Source: https://osv.dev/vulnerability/CVE-2024-56799
Type: osv

## Details
Simofa is a tool to help automate static website building and deployment. Prior to version 0.2.7, due to a design mistake in the RouteLoader class, some API routes may be publicly accessible when they should require authentication. This vulnerability has been patched in v0.2.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56799.json
- https://github.com/TrueWinter/simofa/security/advisories/GHSA-83qw-5qq5-v7pq
- https://nvd.nist.gov/vuln/detail/CVE-2024-56799
- https://github.com/TrueWinter/simofa/commit/1b04ba413a9c1d12a33dd50a32f67345c2fa6f2a
