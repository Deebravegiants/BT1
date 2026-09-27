# [M] OSGeo gdal HDF-EOS Grid File SWapi.c memmove out-of-bounds

## Summary
Severity: Medium
Advisory: BIT-gdal-2026-8084
Aliases: CVE-2026-8084, PYSEC-2026-2153
Ecosystem: Bitnami
Published: 2026-05-11
Source: https://osv.dev/vulnerability/BIT-gdal-2026-8084
Type: osv

## Affected
- Bitnami: `gdal` — affected >=0 <3.13.0

## Details
A vulnerability was determined in OSGeo gdal up to 3.13.0. This vulnerability affects the function memmove of the file frmts/hdf4/hdf-eos/SWapi.c of the component HDF-EOS Grid File Handler. This manipulation causes out-of-bounds read. The attack is restricted to local execution. The exploit has been publicly disclosed and may be utilized. Upgrading to version 3.13.0 is able to resolve this issue. Patch name: a791f70f8eaec540974ec989ca6fb00266b7646c. Upgrading the affected component is advised.

## References
- https://github.com/OSGeo/gdal/
- https://github.com/OSGeo/gdal/commit/a791f70f8eaec540974ec989ca6fb00266b7646c
- https://github.com/OSGeo/gdal/issues/14378
- https://github.com/OSGeo/gdal/releases/tag/v3.13.0RC1
- https://github.com/biniamf/pocs/blob/main/gdal_swfinfo_dimlist_oob-rw
- https://github.com/biniamf/pocs/tree/main/gdal_swfinfo_dimlist_oob-rw
- https://nvd.nist.gov/vuln/detail/CVE-2026-8084
- https://vuldb.com/submit/808034
- https://vuldb.com/vuln/361838
- https://vuldb.com/vuln/361838/cti
