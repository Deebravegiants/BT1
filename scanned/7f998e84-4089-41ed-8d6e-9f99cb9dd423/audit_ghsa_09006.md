# [H] GDAL: scanForGeometryContainers in the netCDF driver allows code execution via a stack-based buffer overflow

## Summary
Severity: High
Advisory: GHSA-wphc-7cm7-8mf7
CVE: CVE-2026-49014
CWE: CWE-121
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-wphc-7cm7-8mf7
Type: github-advisory

## Affected
- PyPI: `gdal` — affected >=3.1.0 <3.13.1

## Details
In GDAL 3.1.0 through 3.13.0, scanForGeometryContainers in the netCDF driver allows code execution via a stack-based buffer overflow. It reads a geometry attribute into a fixed-size stack buffer without validating the attribute length. The attacker embeds the exploit as an oversized geometry attribute in a crafted NetCDF file. This achieves arbitrary code execution on the server running GDAL. This is in frmts/netcdf/netcdfsg.cpp.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-49014
- https://github.com/OSGeo/gdal/issues/14594
- https://github.com/OSGeo/gdal/pull/14598
- https://github.com/OSGeo/gdal/commit/f5ebabc1042f3c59b24e7c8ad45dda242d127f09
- https://github.com/OSGeo/gdal
- https://github.com/OSGeo/gdal/blob/v3.13.1/NEWS.md
- https://github.com/pypa/advisory-database/tree/main/vulns/gdal/PYSEC-2026-193.yaml
