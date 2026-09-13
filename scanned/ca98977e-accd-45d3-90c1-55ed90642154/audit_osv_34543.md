# [M] WeGIA: Broken Access Control in `get_relatorios_socios.php` Endpoint

## Summary
Severity: Medium
Advisory: CVE-2025-61665
Aliases: GHSA-62wp-6qmh-6p5f
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:L/SI:L/SA:N)
Published: 2025-10-02
Source: https://osv.dev/vulnerability/CVE-2025-61665
Type: osv

## Details
WeGIA is an open source web manager with a focus on charitable institutions. Versions 3.4.12 and below contain a Broken Access Control vulnerability, identified in the get_relatorios_socios.php endpoint. This vulnerability allows unauthenticated attackers to directly access sensitive personal and financial information of members without requiring authentication or authorization. This issue is fixed in version 3.5.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61665.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-62wp-6qmh-6p5f
- https://nvd.nist.gov/vuln/detail/CVE-2025-61665
- https://github.com/LabRedesCefetRJ/WeGIA/commit/828f23a6a760a52b8bb8bfd583cc2b23c42da51e
