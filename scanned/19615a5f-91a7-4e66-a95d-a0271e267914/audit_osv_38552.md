# [M] Apache Flink Kubernetes Operator: Server-Side Request Forgery and local file access in Kubernetes Operator

## Summary
Severity: Medium
Advisory: CVE-2026-40564
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-40564
Type: osv

## Details
Files or Directories Accessible to External Parties, Server-Side Request Forgery (SSRF) vulnerability in Apache Flink Kubernetes Operator.

The FlinkSessionJob jarURI is currently not validated so that it points to user-owned files or addresses.  This lets a user with CR create permissions read files from the operator pod's filesystem and pull content from any backing store reachable through Flink's pluggable filesystem layer and access them through the submitted Flink job. Furthermore for fetching from http/https addresses there is currently no allowlist on the URI scheme, no host check, no IP-range restriction, and no protection against pointing the URI at internal or link-local addresses.This issue affects Apache Flink Kubernetes Operator: from 1.3.0 before 1.15.0.

Users are recommended to upgrade to version 1.15.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/05/26/6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40564.json
- https://lists.apache.org/thread/jvxs2kh2o60sl7qkl5nss4r5phzfl4cz
- https://nvd.nist.gov/vuln/detail/CVE-2026-40564
