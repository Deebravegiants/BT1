# [M] OSGeo GDAL vulnerable to out-of-bounds read

## Summary
Severity: Medium
Advisory: JLSEC-2026-770
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/JLSEC-2026-770
Type: osv

## Affected
- Julia: `GDAL_jll` — affected >=0 <305.1300.0+0

## Details
A weakness has been identified in OSGeo gdal up to 3.13.0dev-4. The affected element is the function GDfieldinfo of the file `frmts/hdf4/hdf-eos/GDapi.c`. Executing a manipulation can lead to out-of-bounds read. The attack needs to be launched locally. The exploit has been made available to the public and could be used for attacks. Upgrading to version 3.13.0RC1 is sufficient to fix this issue. This patch is called a791f70f8eaec540974ec989ca6fb00266b7646c. The affected component should be upgraded.

## References
- https://github.com/OSGeo/gdal
- https://github.com/OSGeo/gdal/
- https://github.com/OSGeo/gdal/commit/a791f70f8eaec540974ec989ca6fb00266b7646c
- https://github.com/OSGeo/gdal/issues/14379
- https://github.com/OSGeo/gdal/releases/tag/v3.13.0RC1
- https://github.com/advisories/GHSA-j3f5-rw74-g4rv
- https://github.com/biniamf/pocs/tree/main/gdal-gdapi-gdfinfo-dimlist-oob-read
- https://nvd.nist.gov/vuln/detail/CVE-2026-8088
- https://vuldb.com/submit/808040
- https://vuldb.com/vuln/361841
- https://vuldb.com/vuln/361841/cti
