# [H] UnoPim has Broken Access Control

## Summary
Severity: High
Advisory: GHSA-8p2f-fx4q-75cx
CVE: CVE-2025-55741
CWE: CWE-284, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-08-22
Source: https://github.com/advisories/GHSA-8p2f-fx4q-75cx
Type: github-advisory

## Affected
- Packagist: `unopim/unopim` — affected >=0 <0.3.1

## Details
### Summary
In Unopim, it is possible to create roles and choose the privileges. However, users without the “Delete” privilege for Products cannot delete a single product via the standard endpoint (expected behavior), but can still delete products via the mass-delete endpoint, even when the request contains only one product ID.

**Severity**: High CVSS Score 8.1 (CVSS 3.1 Vector: [AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?vector=AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H&version=3.1))
**Category**: Broken Access Control / Missing Authorization (OWASP A01:2021)
**Impact**: Unauthorized product deletion -> data loss, possible business disruption

### Affected Behavior
**Single delete (enforced):**
**DELETE** `/admin/catalog/products/{id}` returns 401 with "This action is unauthorized" for users lacking the Delete privilege.

**Mass delete (not enforced):**
**POST** `/admin/catalog/products/mass-delete` allows deletion without the Delete privilege. This occurs for both multiple IDs and a single ID submitted to the bulk endpoint.

### PoC
A video was captured in Burp Suite for a proof of concept. The cookies were used directly from Burp Suite and rendered the My Account page to prove what cookies belong to what users. The video PoC is listed in references.

### Impact
Unauthorized product deletion -> data loss, possible business disruption

## References
- https://github.com/unopim/unopim/security/advisories/GHSA-8p2f-fx4q-75cx
- https://nvd.nist.gov/vuln/detail/CVE-2025-55741
- https://github.com/unopim/unopim/commit/c14eebe653aafd8dc713ca729165177e63315989
- https://github.com/unopim/unopim/commit/f49fa630afd36ff61c146b3e5bc7a0808667ca19
- https://github.com/unopim/unopim
- https://www.youtube.com/watch?v=J_WV8fCXlJM
- https://youtu.be/J_WV8fCXlJM
