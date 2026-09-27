# [M] knowns before 0.30.0 Path Traversal via Document API

## Summary
Severity: Medium
Advisory: CVE-2026-86775
Aliases: GHSA-3h35-4jq7-hv45
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86775
Type: osv

## Details
knowns (npm package) versions <= 0.29.1 contain a path traversal vulnerability in the Document API. The HTTP handler in internal/server/routes/docs.go normalizes the user-supplied document path with cleanDocPath(), which strips leading/trailing slashes and the .md suffix but does not neutralize ../ traversal sequences, and internal/storage/doc_store.go then builds the target path with filepath.Join(ds.docsDir(), filepath.FromSlash(doc.Path)+".md") without verifying that the resolved path remains inside the documents directory. In the default deployment, where the Management API is unauthenticated and bound to all interfaces, a remote unauthenticated attacker can supply a traversal payload (for example {"path": "../../../../tmp/knowns_pwn_marker"} to POST /api/docs, or an encoded path to GET /api/docs/...) to read, create, overwrite, or delete arbitrary files with a .md extension anywhere on the host filesystem and to create arbitrary directories via os.MkdirAll. This can expose sensitive data stored in other projects' documentation, corrupt or destroy files, and provide an arbitrary-write primitive that may be chained toward code execution. The issue is fixed in version 0.30.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86775.json
- https://github.com/knowns-dev/knowns/security/advisories/GHSA-3h35-4jq7-hv45
- https://nvd.nist.gov/vuln/detail/CVE-2026-86775
- https://www.vulncheck.com/advisories/knowns-before-0.30.0-path-traversal-via-document-api
