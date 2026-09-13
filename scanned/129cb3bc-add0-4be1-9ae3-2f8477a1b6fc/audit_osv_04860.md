# [M] OSGeo gdal GDapi.c GDfieldinfo out-of-bounds

## Summary
Severity: Medium
Advisory: BIT-gdal-2026-8088
Aliases: CVE-2026-8088, GHSA-j3f5-rw74-g4rv, PYSEC-2026-2156
Ecosystem: Bitnami
Published: 2026-05-11
Source: https://osv.dev/vulnerability/BIT-gdal-2026-8088
Type: osv

## Affected
- Bitnami: `gdal` — affected >=0 <3.13.0

## Details
A weakness has been identified in OSGeo gdal up to 3.13.0. The affected element is the function GDfieldinfo of the file frmts/hdf4/hdf-eos/GDapi.c. Executing a manipulation can lead to out-of-bounds read. The attack needs to be launched locally. The exploit has been made available to the public and could be used for attacks. Upgrading to version 3.13.0 is sufficient to fix this issue. This patch is called a791f70f8eaec540974ec989ca6fb00266b7646c. The affected component should be upgraded.

## References
- https://github.com/OSGeo/gdal/
- https://github.com/OSGeo/gdal/commit/a791f70f8eaec540974ec989ca6fb00266b7646c
- https://github.com/OSGeo/gdal/issues/14379
- https://github.com/OSGeo/gdal/releases/tag/v3.13.0RC1
- https://github.com/biniamf/pocs/tree/main/gdal-gdapi-gdfinfo-dimlist-oob-read
- https://nvd.nist.gov/vuln/detail/CVE-2026-8088
- https://vuldb.com/submit/808040
- https://vuldb.com/vuln/361841
- https://vuldb.com/vuln/361841/cti
