# [M] Apache CouchDB, IBM Cloudant: Information sharing via couchjs processes

## Summary
Severity: Medium
Advisory: BIT-couchdb-2023-26268
Aliases: CVE-2023-26268
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-couchdb-2023-26268
Type: osv

## Affected
- Bitnami: `couchdb` — affected >=3.3.0 <3.3.2

## Details
Design documents with matching document IDs, from databases on the same cluster, may share a mutable Javascript environment when using these design document functions:
  *  validate_doc_update

  *  list

  *  filter

  *  filter views (using view functions as filters)

  *  rewrite

  *  update



This doesn't affect map/reduce or search (Dreyfus) index functions.

Users are recommended to upgrade to a version that is no longer affected by this issue (Apache CouchDB 3.3.2 or 3.2.3).

Workaround: Avoid using design documents from untrusted sources which may attempt to cache or store data in the Javascript environment.

## References
- https://docs.couchdb.org/en/stable/cve/2023-26268.html
- https://lists.apache.org/thread/ldkqs0nhpmho26bdxf4fon7w75hsq5gl
- https://lists.apache.org/thread/r2wvjfysg3d92lhhjd1qh3wfr8mlp0pp
- https://nvd.nist.gov/vuln/detail/CVE-2023-26268
