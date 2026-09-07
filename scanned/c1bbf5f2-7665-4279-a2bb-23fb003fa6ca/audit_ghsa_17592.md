# [M] HKUDS LightRAG allows Path Traversal via function upload_to_input_dir

## Summary
Severity: Medium
Advisory: GHSA-v9w6-9hq9-33ch
CVE: CVE-2025-6773
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-06-27
Source: https://github.com/advisories/GHSA-v9w6-9hq9-33ch
Type: github-advisory

## Affected
- PyPI: `lightrag-hku` — affected >=0 <1.3.8

## Details
A vulnerability was found in HKUDS LightRAG up to 1.3.8. It has been declared as critical. Affected by this vulnerability is the function upload_to_input_dir of the file lightrag/api/routers/document_routes.py of the component File Upload. The manipulation of the argument file.filename leads to path traversal. It is possible to launch the attack on the local host. The identifier of the patch is 60777d535b719631680bcf5d0969bdef79ca4eaf. It is recommended to apply a patch to fix this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6773
- https://github.com/HKUDS/LightRAG/issues/1692
- https://github.com/HKUDS/LightRAG/issues/1692#issuecomment-3009368235
- https://github.com/HKUDS/LightRAG/commit/60777d535b719631680bcf5d0969bdef79ca4eaf
- https://github.com/HKUDS/LightRAG
- https://vuldb.com/?ctiid.314089
- https://vuldb.com/?id.314089
- https://vuldb.com/?submit.601276
