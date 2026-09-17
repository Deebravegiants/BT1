# [M] Unauthenticated Disclosure of PSU HAX CMS Site Listings via haxPsuUsage API Endpoint

## Summary
Severity: Medium
Advisory: GHSA-fvx2-x7ff-fc56
CVE: CVE-2025-48996
CWE: CWE-201
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-06-05
Source: https://github.com/advisories/GHSA-fvx2-x7ff-fc56
Type: github-advisory

## Affected
- npm: `@haxtheweb/open-apis` — affected >=0

## Details
### Summary
An **unauthenticated information disclosure vulnerability** exists in the PSU deployment of HAX CMS via the `haxPsuUsage` API endpoint. This allows **any remote unauthenticated user** to retrieve a full list of PSU websites hosted on HAX CMS. When chained with other authorization issues (e.g., HAX-3), this could assist in targeted attacks such as unauthorized content modification or deletion.

---

### Details
The endpoint [`https://open-apis.hax.cloud/api/services/stats/haxPsuUsage`](https://open-apis.hax.cloud/api/services/stats/haxPsuUsage) returns a list of websites on the PSU instance of HAX CMS. This endpoint is exposed without any authentication or authorization checks.

The source of the issue is in the `haxPsuUsage.js` file, which appears to directly serve the site listing without verifying user identity or access level. This enables anyone with the endpoint URL to enumerate all site instances under the PSU deployment.

This endpoint may have originally been used for internal or statistical purposes but is now publicly accessible, representing a privacy and enumeration risk.

---

### PoC
To reproduce this vulnerability:

1. Open a terminal or browser.
2. Send a GET request to the following endpoint:
   ```bash
   curl https://open-apis.hax.cloud/api/services/stats/haxPsuUsage

---

### Impact

The `haxPsuUsage` endpoint exposes a full list of PSU HAX CMS websites to **any unauthenticated user**, allowing external actors to enumerate all sites under the PSU domain. This alone represents an information disclosure vulnerability.

When **chained with the Lack Of Authorization Checks CVE**, which involves missing authorization checks on key API endpoints, the risk escalates significantly. An **authenticated attacker** can:

- Modify or delete other users' sites via:
  - `createNode()`, `saveNode()`, `deleteNode()`
- Access sensitive metadata or credentials:
  - `getConfig()`, `downloadSite()`
- Clone or remove entire sites:
  - `cloneSite()`, `deleteSite()`, `archiveSite()`

Combined, these issues allow a low-privileged user to **fully compromise any site** in the PSU HAX CMS instance.

This vulnerability chain puts **content integrity, availability, and confidentiality** at risk for potentially hundreds of PSU academic, instructional, and departmental sites.

## References
- https://github.com/haxtheweb/issues/security/advisories/GHSA-fvx2-x7ff-fc56
- https://nvd.nist.gov/vuln/detail/CVE-2025-48996
- https://github.com/haxtheweb/open-apis/commit/06c2e1fbb7131a8fe66aa0600f38dcacae6b7ac7
- https://github.com/haxtheweb/issues
