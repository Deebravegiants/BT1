# [C] Apache Polaris: could broaden vended S3 credentials through wildcard-bearing namespace or table names

## Summary
Severity: Critical
Advisory: CVE-2026-42810
Aliases: GHSA-vxgg-mqx2-3w59
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/CVE-2026-42810
Type: osv

## Details
Apache Polaris accepts literal `*` characters in namespace and table names. When it
later builds temporary S3 access policies for delegated table access, those
same characters appear to be reused unescaped in S3 IAM resource patterns
and
`s3:prefix` conditions.



In S3 IAM policy matching, `*` is treated as a wildcard rather than as
ordinary text. That means temporary credentials issued for one crafted table
can match the storage path of a different table.



In private testing against Polaris 1.4.0 using Polaris' AWS S3 temporary-
credential path on both MinIO and real AWS S3, credentials returned for
crafted tables such as `f*.t1`, `f*.*`, `*.*`, and `foo.*` could reach other
tables' S3 locations.


The confirmed behavior includes:


- reading another table's metadata control file ([Iceberg metadata JSON]);

- listing another table's exact S3 table prefix ([table prefix]);

- and, when write delegation was returned for the crafted table, creating
and
deleting an object under another table's exact S3 table prefix.



A control case using ordinary different names did not allow the same
cross-table access.



A least-privilege AWS S3 variant was also confirmed in which the attacker
principal had no Polaris permissions on the victim table and only the
minimal permissions required to create and use a crafted wildcard table
(namespace-scoped `TABLE_CREATE` and `TABLE_WRITE_DATA` on `*`). In that
setup, direct Polaris access to `foo.t1` remained forbidden, but the
attacker
could still create and load `*.*`, receive delegated S3 credentials, and use
those credentials to list, read, create, and delete objects under `foo.t1`.



In Iceberg, the metadata JSON file is a control file: it tells readers which
data files belong to the table, which snapshots exist, and which table
version
to read. So unauthorized access to it is already a meaningful
confidentiality
problem. The confirmed write-capable variant means the issue is not limited
to
disclosure.

## References
- http://www.openwall.com/lists/oss-security/2026/05/02/11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42810.json
- https://lists.apache.org/thread/gg3qq9sqg4hdjmprqy46p40xmln61dm9
- https://nvd.nist.gov/vuln/detail/CVE-2026-42810
