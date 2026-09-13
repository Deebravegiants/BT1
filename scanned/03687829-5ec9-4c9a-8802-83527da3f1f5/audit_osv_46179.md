# [H] A vulnerability was identified in OSGeo gdal up to 3.13.0dev-4

## Summary
Severity: High
Advisory: JLSEC-2026-768
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/JLSEC-2026-768
Type: osv

## Affected
- Julia: `GDAL_jll` — affected >=0 <305.1300.0+0

## Details
A vulnerability was identified in OSGeo gdal up to 3.13.0dev-4. This issue affects the function SWnentries of the file `frmts/hdf4/hdf-eos/SWapi.c`. Such manipulation of the argument DimensionName leads to heap-based buffer overflow. The attack must be carried out locally. The exploit is publicly available and might be used. Upgrading to version 3.12.4RC1 is capable of addressing this issue. The name of the patch is 9491e794f1757f08063ea2f7a274ad2994afa636. It is advisable to upgrade the affected component.

## References
- https://github.com/OSGeo/gdal
- https://github.com/OSGeo/gdal/
- https://github.com/OSGeo/gdal/commit/9491e794f1757f08063ea2f7a274ad2994afa636
- https://github.com/OSGeo/gdal/issues/14356
- https://github.com/OSGeo/gdal/pull/14361
- https://github.com/OSGeo/gdal/releases/tag/v3.12.4RC1
- https://github.com/advisories/GHSA-72pg-5w29-wjx6
- https://github.com/biniamf/pocs/tree/main/gdal-swinqdims_bof
- https://nvd.nist.gov/vuln/detail/CVE-2026-8086
- https://vuldb.com/submit/808038
- https://vuldb.com/vuln/361839
- https://vuldb.com/vuln/361839/cti
