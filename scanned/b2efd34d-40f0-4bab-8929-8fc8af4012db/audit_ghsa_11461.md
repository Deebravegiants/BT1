# [H] Parse Server's LiveQuery bypasses CLP pointer permission enforcement

## Summary
Severity: High
Advisory: GHSA-fph2-r4qg-9576
CVE: CVE-2026-33421
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-fph2-r4qg-9576
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.42
- npm: `parse-server` — affected >=0 <8.6.53

## Details
### Impact

Parse Server's LiveQuery WebSocket interface does not enforce Class-Level Permission (CLP) pointer permissions (`readUserFields` and `pointerFields`). Any authenticated user can subscribe to LiveQuery events and receive real-time updates for all objects in classes protected by pointer permissions, regardless of whether the pointer fields on those objects point to the subscribing user. This bypasses the intended read access control, allowing unauthorized access to potentially sensitive data that is correctly restricted via the REST API.

### Patches

The LiveQuery server now enforces pointer permissions on each event. After the existing check passes (which defers pointer permissions by design), the fix checks whether any configured pointer field on the object points to the subscribing user. Events for objects that don't match are silently skipped, consistent with how ACL mismatches are handled.

### Workarounds

Use ACLs on individual objects to restrict read access instead of relying solely on CLP pointer permissions. ACLs are enforced by LiveQuery.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-fph2-r4qg-9576
- https://nvd.nist.gov/vuln/detail/CVE-2026-33421
- https://github.com/parse-community/parse-server/pull/10250
- https://github.com/parse-community/parse-server/pull/10252
- https://github.com/parse-community/parse-server/commit/6c3317aca6eb618ac48f999021ae3ef7766ad1ea
- https://github.com/parse-community/parse-server/commit/976dad109f3fe3fbd0a3a35ef62e7a5d35eb0bee
- https://github.com/parse-community/parse-server
