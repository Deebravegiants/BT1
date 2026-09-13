# [M] Semi-blind Server-Side Request Forgery in dhis2-core

## Summary
Severity: Medium
Advisory: CVE-2022-41949
Aliases: GHSA-6qh9-rxc8-7943
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2022-12-08
Source: https://osv.dev/vulnerability/CVE-2022-41949
Type: osv

## Details
DHIS 2 is an open source information system for data capture, management, validation, analytics and visualization. In affected versions an authenticated DHIS2 user can craft a request to DHIS2 to instruct the server to make requests to external resources (like third party servers). This could allow an attacker, for example, to identify vulnerable services which might not be otherwise exposed to the public internet or to determine whether a specific file is present on the DHIS2 server. DHIS2 administrators should upgrade to the following hotfix releases: 2.36.12.1, 2.37.8.1, 2.38.2.1, 2.39.0.1. At this time, there is no known workaround or mitigation for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41949.json
- https://github.com/dhis2/dhis2-core/security/advisories/GHSA-6qh9-rxc8-7943
- https://nvd.nist.gov/vuln/detail/CVE-2022-41949
- https://github.com/dhis2/dhis2-core/commit/dc3166c216da53e12a16bfdc51055823b838c1c3
