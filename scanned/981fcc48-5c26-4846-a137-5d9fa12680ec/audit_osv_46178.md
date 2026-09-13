# [M] A vulnerability was determined in OSGeo gdal up to 3.13.0dev-4

## Summary
Severity: Medium
Advisory: JLSEC-2026-767
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/JLSEC-2026-767
Type: osv

## Affected
- Julia: `GDAL_jll` — affected >=0 <305.1300.0+0

## Details
A vulnerability was determined in OSGeo gdal up to 3.13.0dev-4. This vulnerability affects the function memmove of the file `frmts/hdf4/hdf-eos/SWapi.c` of the component HDF-EOS Grid File Handler. This manipulation causes out-of-bounds read. The attack is restricted to local execution. The exploit has been publicly disclosed and may be utilized. Upgrading to version 3.13.0RC1 is able to resolve this issue. Patch name: a791f70f8eaec540974ec989ca6fb00266b7646c. Upgrading the affected component is advised.

## References
- https://github.com/OSGeo/gdal
- https://github.com/OSGeo/gdal/
- https://github.com/OSGeo/gdal/commit/a791f70f8eaec540974ec989ca6fb00266b7646c
- https://github.com/OSGeo/gdal/issues/14378
- https://github.com/OSGeo/gdal/releases/tag/v3.13.0RC1
- https://github.com/advisories/GHSA-jmvp-7877-wr2f
- https://github.com/biniamf/pocs/blob/main/gdal_swfinfo_dimlist_oob-rw
- https://github.com/biniamf/pocs/tree/main/gdal_swfinfo_dimlist_oob-rw
- https://nvd.nist.gov/vuln/detail/CVE-2026-8084
- https://vuldb.com/submit/808034
- https://vuldb.com/vuln/361838
- https://vuldb.com/vuln/361838/cti
