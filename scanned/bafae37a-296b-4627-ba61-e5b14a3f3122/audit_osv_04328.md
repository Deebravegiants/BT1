# [H] Privilege escalation vulnerability when using HTML attachments

## Summary
Severity: High
Advisory: BIT-couchdb-2021-38295
Aliases: CVE-2021-38295
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-couchdb-2021-38295
Type: osv

## Affected
- Bitnami: `couchdb` — affected >=0 <3.1.2

## Details
In Apache CouchDB, a malicious user with permission to create documents in a database is able to attach a HTML attachment to a document. If a CouchDB admin opens that attachment in a browser, e.g. via the CouchDB admin interface Fauxton, any JavaScript code embedded in that HTML attachment will be executed within the security context of that admin. A similar route is available with the already deprecated _show and _list functionality. This privilege escalation vulnerability allows an attacker to add or remove data in any database or make configuration changes. This issue affected Apache CouchDB prior to 3.1.2

## References
- https://docs.couchdb.org/en/stable/cve/2021-38295.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-38295
