# [M] Sqlite: use-after-free bug in jsonparseaddnodearray

## Summary
Severity: Medium
Advisory: BIT-sqlite-2024-0232
Aliases: CVE-2024-0232
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-sqlite-2024-0232
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=3.43.0

## Details
A heap use-after-free issue has been identified in SQLite in the jsonParseAddNodeArray() function in sqlite3.c. This flaw allows a local attacker to leverage a victim to pass specially crafted malicious input to the application, potentially causing a crash and leading to a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2024-0232
- https://bugzilla.redhat.com/show_bug.cgi?id=2243754
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QDCMYQ3J45NHQ4EJREM3BJNNKB5BK4Y7/
- https://security.netapp.com/advisory/ntap-20240315-0007/
- https://nvd.nist.gov/vuln/detail/CVE-2024-0232
