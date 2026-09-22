# [H] Helm vulnerable to Denial of service via NULL Pointer Dereference

## Summary
Severity: High
Advisory: BIT-helm-2022-23525
Aliases: CVE-2022-23525, GHSA-53c4-hhmh-vw5q, GO-2022-1165
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-helm-2022-23525
Type: osv

## Affected
- Bitnami: `helm` — affected >=3.0.0 <3.10.3

## Details
Helm is a tool for managing Charts, pre-configured Kubernetes resources. Versions prior to 3.10.3 are subject to NULL Pointer Dereference in the _repo_package. The _repo_ package contains a handler that processes the index file of a repository. For example, the Helm client adds references to chart repositories where charts are managed. The _repo_ package parses the index file of the repository and loads it into structures Go can work with. Some index files can cause array data structures to be created causing a memory violation. Applications that use the _repo_ package in the Helm SDK to parse an index file can suffer a Denial of Service when that input causes a panic that cannot be recovered from. The Helm Client will panic with an index file that causes a memory violation panic. Helm is not a long running service so the panic will not affect future uses of the Helm client. This issue has been patched in 3.10.3. SDK users can validate index files that are correctly formatted before passing them to the _repo_ functions.

## References
- https://github.com/helm/helm/commit/638ebffbc2e445156f3978f02fd83d9af1e56f5b
- https://github.com/helm/helm/security/advisories/GHSA-53c4-hhmh-vw5q
- https://nvd.nist.gov/vuln/detail/CVE-2022-23525
