# [H] Path Traversal in DKPro Core

## Summary
Severity: High
Advisory: GHSA-23gj-368h-92pq
CVE: CVE-2019-11082
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-05-29
Source: https://github.com/advisories/GHSA-23gj-368h-92pq
Type: github-advisory

## Affected
- Maven: `de.tudarmstadt.ukp.dkpro.core:de.tudarmstadt.ukp.dkpro.core.api.datasets-asl` — affected >=0

## Details
core/api/datasets/internal/actions/Explode.java in the Dataset API in DKPro Core through 1.10.0 allows Directory Traversal, resulting in the overwrite of local files with the contents of an archive.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11082
- https://github.com/dkpro/dkpro-core/issues/1325
