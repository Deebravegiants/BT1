# [M] Cluster Existence Oracle via Unauthenticated Import Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-55998
Aliases: GHSA-23h9-rr79-r3gh
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-55998
Type: osv

## Details
The endpoint /v3/import/{token}_{clusterId}.yaml retrieves the cluster object before validating the token. When a valid cluster ID references a cluster that has private registry secrets configured, a nil pointer dereference in pkg/systemtemplate/private_registry.go causes the request to return HTTP 502 Bad Gateway. For cluster IDs that do not exist, the endpoint returns HTTP 200. This observable difference in response codes constitutes a reliable enumeration oracle.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55998.json
- https://github.com/rancher/rancher/security/advisories/GHSA-23h9-rr79-r3gh
- https://nvd.nist.gov/vuln/detail/CVE-2026-55998
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2026-55998
