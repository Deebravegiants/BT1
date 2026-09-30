# [M] APITable through 1.13.0-beta.1 Missing Authentication on the Internal Organization Load or Search Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-84485
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84485
Type: osv

## Details
APITable through 1.13.0-beta.1 exposes the internal organization loadOrSearch endpoint without authentication, allowing unauthenticated attackers to retrieve member names, email addresses, and team hierarchy. Attackers can query the endpoint with space identifiers obtained from shared links or public templates to enumerate the complete member directory of any workspace.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84485.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-84485
- https://www.vulncheck.com/advisories/apitable-through-1.13.0-beta.1-missing-authentication-on-the-internal-organization-load-or-search-endpoint
- https://github.com/apitable/apitable
- https://github.com/apitable/apitable/blob/88b24ce9f359cc434778be75d03603182882dc76/backend-server/application/src/main/java/com/apitable/internal/controller/InternalOrganizationController.java#L58
- https://github.com/apitable/apitable/blob/88b24ce9f359cc434778be75d03603182882dc76/backend-server/application/src/main/java/com/apitable/shared/context/LoginContext.java
- https://github.com/apitable/apitable/blob/88b24ce9f359cc434778be75d03603182882dc76/backend-server/application/src/main/java/com/apitable/shared/interceptor/ResourceInterceptor.java#L85
