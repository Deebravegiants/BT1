# [H] Outline has IDOR in document share creation that allows unauthorized access to private documents across workspaces

## Summary
Severity: High
Advisory: CVE-2026-41649
Aliases: GHSA-23jj-rp48-w7q7
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-04-28
Source: https://osv.dev/vulnerability/CVE-2026-41649
Type: osv

## Details
Outline is a service that allows for collaborative documentation. The `shares.create` API endpoint starting in version 0.86.0 and prior to version 1.7.0 has an insecure direct object reference.. When both `collectionId` and `documentId` are provided in the request, the authorization logic only checks access to the collection, completely ignoring the document. This allows an authenticated attacker to generate a valid public share link for any document on the platform, including documents belonging to other workspaces. The full document contents can then be retrieved via the `documents.info` endpoint. Version 1.7.0 contains a patch.

## References
- https://github.com/outline/outline/releases/tag/v1.7.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41649.json
- https://github.com/outline/outline/security/advisories/GHSA-23jj-rp48-w7q7
- https://nvd.nist.gov/vuln/detail/CVE-2026-41649
- https://github.com/outline/outline/commit/1b91a295e10f58a1088c54f533773788325ff460
