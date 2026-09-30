# [C] Apache Polaris: could broaden vended GCS credentials through unescaped identifier content in access-boundary CEL conditions

## Summary
Severity: Critical
Advisory: CVE-2026-42811
Aliases: GHSA-fc3h-c6h7-r83j
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/CVE-2026-42811
Type: osv

## Details
In plain terms, Apache Polaris is supposed to issue short-lived GCS credentials
that
only work for one table's files, but a crafted namespace or table name can
cause those credentials to work across the configured bucket instead.


Apache Polaris builds Google Cloud Storage downscoped credentials by creating a
Credential Access Boundary (CAB) with CEL conditions that are intended to
restrict access to the requested table's storage path.



The relevant CEL string is built from the bucket name and the table path.
That
table path is derived from namespace and table identifiers. In current code,
that path appears to be inserted into the CEL expression without escaping.



As a result, a namespace or table identifier containing a single quote and
other URI-safe CEL fragments can break out of the intended quoted string and
change the meaning of the CEL condition.



In private testing against Polaris 1.4.0 on real Google Cloud Storage, it was confirmed that Polaris accepted a crafted identifier and returned delegated
GCS
credentials whose CEL path restriction had effectively collapsed.


Those delegated credentials could then:


- list another table's object prefix;

- read another table's metadata control file (Iceberg metadata JSON);

- create and delete an object under another table's object prefix;

- and also list, read, create, and delete objects under an unrelated
external
prefix in the same bucket that was not part of any table path.



That last point is important. The issue is not limited to "another table".
In
the confirmed setup, once Apache Polaris returned credentials for the crafted
table,
the path restriction inside the configured bucket was effectively gone.

The practical effect is that temporary credentials for one crafted table
can be
broader than the table Polaris was asked to authorize, and can become
effectively bucket-wide within the configured bucket.



The current GCS testing used a Polaris principal with broad catalog
privileges for setup. A separate least-privilege Polaris RBAC variant
has not yet been tested on GCS. However, the storage-credential
broadening behavior itself has been confirmed on GCS.

## References
- http://www.openwall.com/lists/oss-security/2026/05/02/12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42811.json
- https://lists.apache.org/thread/hovn5hmkj9wj7v9cd8sn67svg03klgvg
- https://nvd.nist.gov/vuln/detail/CVE-2026-42811
