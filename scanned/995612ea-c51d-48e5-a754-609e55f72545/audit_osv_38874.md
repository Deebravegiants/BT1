# [H] Open edX Platform: Server-Side Request Forgery (SSRF) in SAML Provider Data Sync Endpoint

## Summary
Severity: High
Advisory: CVE-2026-42858
Aliases: GHSA-328g-7h4g-r2m9
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-42858
Type: osv

## Details
Open edX Platform enables the authoring and delivery of online learning at any scale. The sync_provider_data endpoint in SAMLProviderDataViewSet allows authenticated Enterprise Admin users to supply an arbitrary URL via the metadata_url POST parameter. This URL is passed directly to requests.get() in fetch_metadata_xml() without any URL validation, IP filtering, or scheme enforcement. An attacker with Enterprise Admin privileges can force the server to make HTTP requests to internal network services, cloud metadata endpoints (e.g., AWS 169.254.169.254), or other attacker-controlled destinations. This vulnerability is fixed by commit 6fda1f120ff5a590d120ae1180185525f399c6d0 and 70a56246dd9c9df57c596e64bdd8a11b1d9da054.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42858.json
- https://github.com/openedx/openedx-platform/security/advisories/GHSA-328g-7h4g-r2m9
- https://nvd.nist.gov/vuln/detail/CVE-2026-42858
- https://github.com/openedx/openedx-platform/commit/6fda1f120ff5a590d120ae1180185525f399c6d0
- https://github.com/openedx/openedx-platform/commit/70a56246dd9c9df57c596e64bdd8a11b1d9da054
