# [M] A vulnerability has been found in OSGeo gdal up to 3.13.0dev-4

## Summary
Severity: Medium
Advisory: JLSEC-2026-772
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/JLSEC-2026-772
Type: osv

## Affected
- Julia: `GDAL_jll` — affected >=0 <305.1300.0+0

## Details
A vulnerability has been found in OSGeo gdal up to 3.13.0dev-4. Affected by this issue is the function GDSDfldsrch of the file `frmts/hdf4/hdf-eos/GDapi.c` of the component Grid File Handler. The manipulation leads to heap-based buffer overflow. An attack has to be approached locally. The exploit has been disclosed to the public and may be used. Upgrading to version 3.13.0RC1 can resolve this issue. The identifier of the patch is 3e04c0385630e4d42517046d9a4967dfccfeb7fd. It is suggested to upgrade the affected component.

## References
- https://github.com/OSGeo/gdal
- https://github.com/OSGeo/gdal/
- https://github.com/OSGeo/gdal/commit/3e04c0385630e4d42517046d9a4967dfccfeb7fd
- https://github.com/OSGeo/gdal/issues/14399
- https://github.com/OSGeo/gdal/releases/tag/v3.13.0RC1
- https://github.com/advisories/GHSA-8q76-c96g-j64j
- https://github.com/biniamf/pocs/tree/main/gdal-gdsdfldsrch_oob-read
- https://nvd.nist.gov/vuln/detail/CVE-2026-8213
- https://vuldb.com/submit/808128
- https://vuldb.com/vuln/362430
- https://vuldb.com/vuln/362430/cti
