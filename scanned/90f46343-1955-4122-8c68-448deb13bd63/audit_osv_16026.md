# [H] CVE-2019-25050

## Summary
Severity: High
Advisory: CVE-2019-25050
Aliases: PYSEC-2021-888
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-20
Source: https://osv.dev/vulnerability/CVE-2019-25050
Type: osv

## Details
netCDF in GDAL 2.4.2 through 3.0.4 has a stack-based buffer overflow in nc4_get_att (called from nc4_get_att_tc and nc_get_att_text) and in uffd_cleanup (called from netCDFDataset::~netCDFDataset and netCDFDataset::~netCDFDataset).

## References
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/gdal/OSV-2020-392.yaml
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/gdal/OSV-2020-420.yaml
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=15143
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=15156
- https://github.com/OSGeo/gdal/commit/27b9bf644bcf1208f7d6594bdd104cc8a8bb0646
- https://github.com/OSGeo/gdal/commit/767e3a56144f676ca738ef8f700e0e56035bd05a
