# [H] milvus-io milvus Grantee ID Hash kv_catalog.go weak hash

## Summary
Severity: High
Advisory: BIT-milvus-2026-10814
Aliases: CVE-2026-10814, GHSA-jh6h-v6mp-h22v, GO-2026-5999
Ecosystem: Bitnami
Published: 2026-06-11
Source: https://osv.dev/vulnerability/BIT-milvus-2026-10814
Type: osv

## Affected
- Bitnami: `milvus` — affected >=0 <2.6.14

## Details
A vulnerability has been found in milvus-io milvus up to 2.6.13. This vulnerability affects unknown code of the file internal/metastore/kv/rootcoord/kv_catalog.go of the component Grantee ID Hash Handler. The manipulation leads to use of weak hash. The attack needs to be performed locally. The attack's complexity is rated as high. It is stated that the exploitability is difficult. The exploit has been disclosed to the public and may be used. The identifier of the patch is 3d932f1c3e065351c4440c27abe1e6479752544d. Applying a patch is the recommended action to fix this issue.

## References
- https://github.com/milvus-io/milvus/
- https://github.com/milvus-io/milvus/commit/3d932f1c3e065351c4440c27abe1e6479752544d
- https://github.com/milvus-io/milvus/issues/49857
- https://github.com/milvus-io/milvus/pull/50060
- https://nvd.nist.gov/vuln/detail/CVE-2026-10814
- https://vuldb.com/cve/CVE-2026-10814
- https://vuldb.com/submit/831645
- https://vuldb.com/vuln/368262
- https://vuldb.com/vuln/368262/cti
