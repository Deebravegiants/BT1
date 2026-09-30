# [M] Kamaji: SQL injection via unescaped datastore identifiers in PostgreSQL/MySQL drivers

## Summary
Severity: Medium
Advisory: CVE-2026-62845
Aliases: GHSA-r47v-ppwp-fh4r
CVSS: 4.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-62845
Type: osv

## Details
Kamaji is the Hosted Control Plane Manager for Kubernetes. Prior to 26.7.4-edge, the PostgreSQL and MySQL datastore drivers build DDL statements by interpolating the user-supplied DataStoreUsername/DataStoreSchema directly into SQL via fmt.Sprintf, without escaping identifiers. These fields have no format validation, so a value containing a quote character breaks out of the quoted identifier — SQL injection executed over Kamaji's root connection to the shared datastore. etcd driver is not affected.This issue is fixed in version 26.7.4-edge.

## References
- https://github.com/clastix/kamaji/releases/tag/26.7.4-edge
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62845.json
- https://github.com/clastix/kamaji/security/advisories/GHSA-r47v-ppwp-fh4r
- https://nvd.nist.gov/vuln/detail/CVE-2026-62845
- https://github.com/clastix/kamaji/commit/6a9f3e10ae408e7948e2aca2db694791a299e79c
