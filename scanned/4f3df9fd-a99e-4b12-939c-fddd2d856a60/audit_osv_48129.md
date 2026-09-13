# [H] CVE-2017-18359

## Summary
Severity: High
Advisory: CVE-2017-18359
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-25
Source: https://osv.dev/vulnerability/CVE-2017-18359
Type: osv

## Details
PostGIS 2.x before 2.3.3, as used with PostgreSQL, allows remote attackers to cause a denial of service via crafted ST_AsX3D function input, as demonstrated by an abnormal server termination for "SELECT ST_AsX3D('LINESTRING EMPTY');" because empty geometries are mishandled.

## References
- https://lists.debian.org/debian-lts-announce/2019/01/msg00030.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00020.html
- https://trac.osgeo.org/postgis/changeset/15444
- https://trac.osgeo.org/postgis/changeset/15445
- https://trac.osgeo.org/postgis/ticket/3704
