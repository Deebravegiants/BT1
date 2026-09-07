# [C] Apache Polaris has an Improper Input Validation issue

## Summary
Severity: Critical
Advisory: GHSA-w76p-3cgp-qfcm
CVE: CVE-2026-42812
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-w76p-3cgp-qfcm
Type: github-advisory

## Affected
- Maven: `org.apache.polaris:polaris-runtime-service` — affected >=0.9.0 <1.4.1

## Details
In Apache Iceberg, the table's metadata files are control files: they tell readers which data files belong to the table and which table version to read.

`write.metadata.path` is an optional table property that tells Polaris where to write those metadata files. For a table already registered in a Polaris-managed catalog, changing only that property through an `ALTER TABLE`-style settings change (not a row-level `INSERT`, `SELECT`, `UPDATE`, or `DELETE`) bypasses the commit-time branch that is supposed to revalidate storage locations.

The full persisted / credential-vending variant requires the affected catalog to have `polaris.config.allow.unstructured.table.location=true`, with `allowedLocations` broad enough to include the attacker-chosen target.

`allowedLocations` is the admin-configured allowlist of storage paths that the catalog is allowed to use. Public project materials suggest that this flag is a real supported compatibility / layout mode, not just a contrived lab-only prerequisite.

In that configuration, a user who can change table settings can cause Apache Polaris itself to write new table metadata to an attacker-chosen reachable storage location before the intended location-validation branch runs.

If the later concrete-path validation also accepts that location, Polaris persists the resulting metadata path into stored table state. Later table-load and credential APIs can then return temporary cloud-storage credentials for the same location without revalidating it. In plain terms, Polaris can later hand out temporary storage access for the same attacker-chosen area.

That attacker-chosen area does not need to be limited to the poisoned table's own files. If it is a broader storage prefix, another table's prefix, or, depending on configuration or provider behavior, even a bucket/container root, the resulting disclosure or corruption scope can extend to any data and metadata Polaris can reach there.

The practical consequences are therefore similar to the staged-create credential-vending issue already discussed: data and metadata reachable in that storage scope can be exposed and, if write-capable credentials are later issued, modified, corrupted, or removed. Even before that later credential step, Polaris itself performs the metadata write to the unchecked location.

So the core issue is not only later credential vending. 

The primary defect is that Polaris skips its intended location checks before performing a security-sensitive metadata write when only `write.metadata.path` changes.

When `polaris.config.allow.unstructured.table.location=false`, current code review suggests the later `updateTableLike(...)` validation usually rejects out-of-tree metadata locations before the unsafe path is persisted. That may reduce the persisted / credential-vending variant, but it does not prevent the underlying defect: Polaris still skips the intended pre-write location check when only `write.metadata.path` changes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42812
- https://github.com/apache/polaris/commit/1cdac7b78c0aa6cc6cad4da10a442ae262d1aae3
- https://github.com/apache/polaris/commit/d6bbcc386e61d08ba5df1f820d0724816d84427b
- https://github.com/apache/polaris
- https://lists.apache.org/thread/wxd2wj3p0smvrk84msv317wg5tp3jtw9
- http://www.openwall.com/lists/oss-security/2026/05/02/13
