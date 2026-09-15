# [M] DataEase: Arbitrary SQL execution in preview path (direct data disclosure)

## Summary
Severity: Medium
Advisory: CVE-2026-50030
Aliases: GHSA-j4v5-5gcx-cvfc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-50030
Type: osv

## Details
DataEase is an open source data visualization and analysis tool. Prior to 2.10.23, DataEase SQL preview exposes DatasetDataApi.previewSql/previewSqlCheck through /de2api/datasetData/previewSql, accepts PreviewSqlDTO.sql, PreviewSqlDTO.datasourceId, and PreviewSqlDTO.isCross, then DatasetDataManage.previewSql stores decoded SQL in datasourceRequest.query and CalciteProvider.fetchResultField executes it with prepareStatement(...).executeQuery(), allowing arbitrary readable datasource tables to be queried and returned in preview responses. This issue is fixed in version 2.10.23.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50030.json
- https://github.com/dataease/dataease/security/advisories/GHSA-j4v5-5gcx-cvfc
- https://nvd.nist.gov/vuln/detail/CVE-2026-50030
- https://github.com/dataease/dataease/commit/22930a493d900fe3d8084b3dd4c0125abdb2a847
