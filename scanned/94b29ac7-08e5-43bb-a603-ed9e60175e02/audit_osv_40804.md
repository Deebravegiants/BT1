# [H] NextCRM has RBAC Bypass in MCP Product Tools that Allows Low-Privileged Users to Modify the CRM Product Catalog

## Summary
Severity: High
Advisory: CVE-2026-55550
Aliases: GHSA-wv63-cq38-qg58
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-55550
Type: osv

## Details
NextCRM is open-source customer relationship management (CRM) software. The CRM product catalog is an organization-wide business object. Normal application server actions restrict product creation, update, and deletion to `manager` and `admin` roles. However, in version 0.12.1, the MCP product tools expose the same write operations through `/api/mcp/mcp` using user-generated Bearer tokens and do not enforce role checks. Any authenticated low-privileged user who can generate an MCP API token can create, modify, archive, or soft-delete products in the shared CRM product catalog. Version 0.12.3 contains a fix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55550.json
- https://github.com/pdovhomilja/nextcrm-app/security/advisories/GHSA-wv63-cq38-qg58
- https://nvd.nist.gov/vuln/detail/CVE-2026-55550
