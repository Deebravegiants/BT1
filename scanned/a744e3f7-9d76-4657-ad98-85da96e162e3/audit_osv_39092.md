# [H] Outline: IDOR in subscriptions.create allows cross-tenant subscription on private documents (sibling of GHSA-23jj-rp48-w7q7)

## Summary
Severity: High
Advisory: CVE-2026-43890
Aliases: GHSA-gf8h-cv9v-q4fw
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-43890
Type: osv

## Details
Outline is a service that allows for collaborative documentation. From 0.84.0 to 1.7.0, the subscriptions.create API endpoint in server/routes/api/subscriptions/subscriptions.ts exhibits a broken authorization pattern. When both collectionId and documentId are supplied in the request, the route handler authorizes ONLY the collection branch (line 125 if (collectionId)), while the downstream subscriptionCreator command at server/commands/subscriptionCreator.ts writes the subscription against the documentId (which was never validated). The result is a subscription record pinning the attacker's user to a victim document the attacker has no read access to, on any team in the instance. The schema (server/routes/api/subscriptions/schema.ts) only enforces "at least one of collectionId/documentId" via .refine() — it does NOT enforce mutual exclusivity, so passing both is a valid, schema-conforming request. This vulnerability is fixed in 1.7.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43890.json
- https://github.com/outline/outline/security/advisories/GHSA-gf8h-cv9v-q4fw
- https://nvd.nist.gov/vuln/detail/CVE-2026-43890
