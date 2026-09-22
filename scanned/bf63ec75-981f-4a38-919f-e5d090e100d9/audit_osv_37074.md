# [M] IDOR in GraphQL userCollection Query Exposes Other Users' Private Collections

## Summary
Severity: Medium
Advisory: CVE-2026-28217
Aliases: GHSA-m5pg-r4jp-qq75
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-28217
Type: osv

## Details
hoppscotch is an open source API development ecosystem. Prior to version 2026.2.0, the `userCollection` GraphQL query accepts an arbitrary collection ID and returns the full collection data — including title, type, and the serialized `data` field containing HTTP requests with headers and potentially secrets — to any authenticated user, without verifying that the requesting user owns the collection. This is an Insecure Direct Object Reference (IDOR) caused by a missing authorization check that exists on every other operation in the same resolver. Version 2026.2.0 fixes the issue.

## References
- https://github.com/hoppscotch/hoppscotch/releases/tag/2026.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28217.json
- https://github.com/hoppscotch/hoppscotch/security/advisories/GHSA-m5pg-r4jp-qq75
- https://nvd.nist.gov/vuln/detail/CVE-2026-28217
