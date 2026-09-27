# [M] BIT-gdal-2025-29480

## Summary
Severity: Medium
Advisory: BIT-gdal-2025-29480
Aliases: CVE-2025-29480, PYSEC-2025-117
Ecosystem: Bitnami
Published: 2025-04-16
Source: https://osv.dev/vulnerability/BIT-gdal-2025-29480
Type: osv

## Affected
- Bitnami: `gdal` — affected >=3.10.2 <3.10.3

## Details
Buffer Overflow vulnerability in gdal 3.10.2 allows a local attacker to cause a denial of service via the OGRSpatialReference::Release function. NOTE: the Supplier indicates that the report is invalid and could not be reproduced.

## References
- https://github.com/lmarch2/poc/blob/main/gdal/gdal.md
- https://nvd.nist.gov/vuln/detail/CVE-2025-29480
- https://github.com/OSGeo/gdal/issues/12188#issuecomment-2847873794
