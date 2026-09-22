# [H] Kestra: Path traversal via URL-encoded "%2E%2E" in execution and namespace file endpoints allows arbitrary file read

## Summary
Severity: High
Advisory: CVE-2026-45807
Aliases: GHSA-3529-p4wf-xp79
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-45807
Type: osv

## Details
Kestra is an open-source, event-driven orchestration platform. Prior to 1.0.43 and 1.3.19, several Kestra API endpoints accept a kestra:// URI from the client and pass it through StorageInterface.parentTraversalGuard before reading the underlying file from the local storage backend. The guard only inspects the literal URI.toString(), so a URL-encoded .. written as %2E%2E slips through. The downstream code then calls URI.getPath(), which decodes %2E%2E back to .., and the resulting path is handed to Paths.get(...) without normalization. The OS resolves the .. segments at open(2) time, so an authenticated user with a single execution can read any file the Kestra process has access to on the host filesystem (/etc/passwd, mounted secrets, other tenants' execution outputs, etc.). This vulnerability is fixed in 1.0.43 and 1.3.19.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45807.json
- https://github.com/kestra-io/kestra/security/advisories/GHSA-3529-p4wf-xp79
- https://nvd.nist.gov/vuln/detail/CVE-2026-45807
