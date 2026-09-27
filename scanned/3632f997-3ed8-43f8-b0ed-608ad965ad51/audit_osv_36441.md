# [M] FOSSBilling: Broken Authorization in Client Transaction and Order Listings

## Summary
Severity: Medium
Advisory: CVE-2026-23513
Aliases: GHSA-xcrv-cccw-r65v
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-23513
Type: osv

## Details
FOSSBilling is a free, open-source billing and client management system. In versions 0.7.2 and prior, a query-construction flaw in client list endpoints allowed authenticated clients to bypass tenant scoping and retrieve other clients’ data. Details
In ServiceTransaction::getSearchQuery() and Order\Service::getSearchQuery(), OR-based search/action filters were appended without grouping, allowing SQL operator precedence to evaluate OR clauses independently of the enforced client_id constraint. Crafted requests could therefore return records and metadata belonging to other clients, including identifiers, amounts, status, timestamps, and related fields. This issue was fixed in version 0.8.0.

## References
- https://github.com/FOSSBilling/FOSSBilling/releases/tag/0.8.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23513.json
- https://github.com/FOSSBilling/FOSSBilling/security/advisories/GHSA-xcrv-cccw-r65v
- https://nvd.nist.gov/vuln/detail/CVE-2026-23513
