# [C] ALPINE-CVE-2017-10989

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-10989
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-10989
Type: osv

## Affected
- Alpine:v3.3: `sqlite` — affected >=0 <3.13.0-r1
- Alpine:v3.4: `sqlite` — affected >=0 <3.13.0-r1
- Alpine:v3.5: `sqlite` — affected >=0 <3.15.2-r1
- Alpine:v3.6: `sqlite` — affected >=0 <3.20.0

## Details
The getNodeSize function in ext/rtree/rtree.c in SQLite through 3.19.3, as used in GDAL and other products, mishandles undersized RTree blobs in a crafted database, leading to a heap-based buffer over-read or possibly unspecified other impact.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-10989
