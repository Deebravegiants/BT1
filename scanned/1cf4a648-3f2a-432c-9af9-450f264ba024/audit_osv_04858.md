# [H] OSGeo gdal SWapi.c SWnentries heap-based overflow

## Summary
Severity: High
Advisory: BIT-gdal-2026-8086
Aliases: CVE-2026-8086, PYSEC-2026-2154
Ecosystem: Bitnami
Published: 2026-05-11
Source: https://osv.dev/vulnerability/BIT-gdal-2026-8086
Type: osv

## Affected
- Bitnami: `gdal` — affected >=0 <3.13.0

## Details
A vulnerability was identified in OSGeo gdal up to 3.13.0. This issue affects the function SWnentries of the file frmts/hdf4/hdf-eos/SWapi.c. Such manipulation of the argument DimensionName leads to heap-based buffer overflow. The attack must be carried out locally. The exploit is publicly available and might be used. Upgrading to version 3.12.4 is capable of addressing this issue. The name of the patch is 9491e794f1757f08063ea2f7a274ad2994afa636. It is advisable to upgrade the affected component.

## References
- https://github.com/OSGeo/gdal/
- https://github.com/OSGeo/gdal/commit/9491e794f1757f08063ea2f7a274ad2994afa636
- https://github.com/OSGeo/gdal/issues/14356
- https://github.com/OSGeo/gdal/pull/14361
- https://github.com/OSGeo/gdal/releases/tag/v3.12.4RC1
- https://github.com/biniamf/pocs/tree/main/gdal-swinqdims_bof
- https://nvd.nist.gov/vuln/detail/CVE-2026-8086
- https://vuldb.com/submit/808038
- https://vuldb.com/vuln/361839
- https://vuldb.com/vuln/361839/cti
