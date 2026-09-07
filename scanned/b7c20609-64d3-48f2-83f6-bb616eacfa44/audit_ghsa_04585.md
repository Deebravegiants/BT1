# [M] parse-server: Relation `$relatedTo` query bypasses `protectedFields` and owning-object ACL

## Summary
Severity: Medium
Advisory: GHSA-wmwx-jr2p-4j4r
CVE: CVE-2026-53726
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-wmwx-jr2p-4j4r
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.9.1-alpha.6
- npm: `parse-server` — affected >=0 <8.6.80

## Details
### Impact

A relation query using the `$relatedTo` operator could read the membership of a `Relation` field even when that field was hidden from the requesting client by `protectedFields`, and even when the object owning the relation was not readable by the client under its ACL or class-level permissions. The request requires only the public API credentials that Parse clients normally carry — no user session, master key, or Cloud Code is needed.

As a result, an unauthenticated client who knows or obtains the owning object's `objectId` could enumerate the objects linked through a protected relation, or combine the operator with an `objectId` constraint to use it as a membership oracle — confirming whether a specific object is linked to a private parent. This affects applications that rely on `protectedFields` or object ACLs to keep `Relation` membership confidential, such as private group memberships, block lists, or account-to-resource associations.

### Patches

The relation query path now authorizes `$relatedTo` against the owning object before reading the relation join table, using the caller's authentication context. The relation key is checked against the owning class's `protectedFields` (the query is rejected if the key is protected), and the owning object must be readable by the caller under its class-level permissions, ACL, and pointer permissions; otherwise the relation returns no results. Master and maintenance requests are unaffected. The check is applied consistently whether `$relatedTo` is used at the top level or nested within `$or`, `$and`, or `$nor`.

### Workarounds

There is no complete workaround without upgrading. As mitigation, applications can avoid exposing sensitive membership through `Relation` fields to untrusted clients, or enforce access on the queried class in a `beforeFind` trigger.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-wmwx-jr2p-4j4r
- https://nvd.nist.gov/vuln/detail/CVE-2026-53726
- https://github.com/parse-community/parse-server/pull/10493
- https://github.com/parse-community/parse-server/pull/10494
- https://github.com/parse-community/parse-server
