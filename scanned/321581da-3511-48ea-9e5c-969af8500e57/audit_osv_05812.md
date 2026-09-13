# [M] Path Traversal in Helm Plugin Archive

## Summary
Severity: Medium
Advisory: BIT-helm-2020-4053
Aliases: CVE-2020-4053, GHSA-qq3j-xp49-j73f
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-helm-2020-4053
Type: osv

## Affected
- Bitnami: `helm` — affected >=3.0.0 <3.2.4

## Details
In Helm greater than or equal to 3.0.0 and less than 3.2.4, a path traversal attack is possible when installing Helm plugins from a tar archive over HTTP. It is possible for a malicious plugin author to inject a relative path into a plugin archive, and copy a file outside of the intended directory. This has been fixed in 3.2.4.

## References
- https://github.com/helm/helm/commit/0ad800ef43d3b826f31a5ad8dfbb4fe05d143688
- https://github.com/helm/helm/releases/tag/v3.2.4
- https://github.com/helm/helm/security/advisories/GHSA-qq3j-xp49-j73f
- https://nvd.nist.gov/vuln/detail/CVE-2020-4053
