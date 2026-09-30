# [H] OSGeo gdal GDapi.c GDnentries heap-based overflow

## Summary
Severity: High
Advisory: BIT-gdal-2026-8087
Aliases: CVE-2026-8087, GHSA-h9rh-5ffh-h669, PYSEC-2026-2155
Ecosystem: Bitnami
Published: 2026-05-11
Source: https://osv.dev/vulnerability/BIT-gdal-2026-8087
Type: osv

## Affected
- Bitnami: `gdal` — affected >=0 <3.13.0

## Details
A security flaw has been discovered in OSGeo gdal up to 3.13.0. Impacted is the function GDnentries of the file frmts/hdf4/hdf-eos/GDapi.c. Performing a manipulation of the argument DataFieldName results in heap-based buffer overflow. The attack must be initiated from a local position. The exploit has been released to the public and may be used for attacks. Upgrading to version 3.13.0 is recommended to address this issue. The patch is named 184f77dbcc74118c062c05e464c88161d3c37b9b. You should upgrade the affected component.

## References
- https://github.com/OSGeo/gdal/
- https://github.com/OSGeo/gdal/commit/184f77dbcc74118c062c05e464c88161d3c37b9b
- https://github.com/OSGeo/gdal/issues/14363
- https://github.com/OSGeo/gdal/releases/tag/v3.13.0RC1
- https://github.com/biniamf/pocs/tree/main/gdal-gdinqfields_bof
- https://nvd.nist.gov/vuln/detail/CVE-2026-8087
- https://vuldb.com/submit/808039
- https://vuldb.com/vuln/361840
- https://vuldb.com/vuln/361840/cti
