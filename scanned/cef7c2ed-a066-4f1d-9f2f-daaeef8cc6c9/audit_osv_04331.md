# [M] Apache CouchDB, IBM Cloudant: Privilege Escalation Using _design Documents

## Summary
Severity: Medium
Advisory: BIT-couchdb-2023-45725
Aliases: CVE-2023-45725
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-couchdb-2023-45725
Type: osv

## Affected
- Bitnami: `couchdb` — affected >=0 <3.3.3

## Details
Design document functions which receive a user http request object may expose authorization or session cookie headers of the user who accesses the document.

These design document functions are:
  *    list
  *    show
  *    rewrite
  *    update

An attacker can leak the session component using an HTML-like output, insert the session as an external resource (such as an image), or store the credential in a _local document with an "update" function.

For the attack to succeed the attacker has to be able to insert the design documents into the database, then manipulate a user to access a function from that design document.

Workaround: Avoid using design documents from untrusted sources which may attempt to access or manipulate request object's headers

## References
- https://docs.couchdb.org/en/stable/cve/2023-45725.html
- https://lists.apache.org/thread/pqjq9zt8vq9rsobkc1cow9sqm9vozlrg
- https://nvd.nist.gov/vuln/detail/CVE-2023-45725
