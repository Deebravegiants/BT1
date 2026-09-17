# [H] Kestra: Path traversal in `LocalStorage` allows any authenticated user to read arbitrary server files via the execution file-download API (`\..\` bypasses the `..` guard)

## Summary
Severity: High
Advisory: CVE-2026-49984
Aliases: GHSA-qw4v-6w32-xx9h
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-49984
Type: osv

## Details
Kestra is an open-source, event-driven orchestration platform. Prior to 1.0.45 and 1.3.23, the local internal-storage backend validates user-supplied paths for .. traversal before it converts Windows-style backslashes to forward slashes. An attacker can therefore smuggle a traversal sequence past the guard using backslashes (..\..\..\); the guard sees a harmless string, and the path is only rewritten to ../../../ after validation, immediately before the file is opened. Any authenticated user who can view an execution (the lowest-privilege role) can call GET /api/v1/{tenant}/executions/{executionId}/file?path=… and read any file on the server filesystem readable by the Kestra process, outside the storage sandbox and across every tenant and namespace. This includes the embedded H2 database (all flows, all users, all stored secrets), internal storage of every other tenant/namespace, mounted secret files, and the process environment (/proc/self/environ) which contains configured database and secret-backend credentials. It is a complete breach of Kestra's storage isolation and multi-tenancy boundary. This vulnerability is fixed in 1.0.45 and 1.3.23.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49984.json
- https://github.com/kestra-io/kestra/security/advisories/GHSA-qw4v-6w32-xx9h
- https://nvd.nist.gov/vuln/detail/CVE-2026-49984
