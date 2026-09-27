# [H] GeoServer has an arbitrary file write vulnerability in its Master Password Dump Page

## Summary
Severity: High
Advisory: CVE-2025-52465
Aliases: GHSA-7qmg-grcp-qf25
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2025-52465
Type: osv

## Details
GeoServer is an open source server that allows users to share and edit geospatial data. Prior to versions 2.26.4 and 2.27.3, a vulnerability exists that allows an authenticated administrator with access to GeoServer's security system to pass arbitrary file names to the Master Password Dump web page and create files containing the master password in plaintext. The provided file name must be an absolute path to the target file, the target file can not already exist and all parent directories must already exist. Versions 2.26.4 and 2.27.3 contain a fix. GeoServer installations where the web interface is either disabled or completely removed are not affected since the vulnerability exists in one of the web pages.

## References
- https://osgeo-org.atlassian.net/browse/GEOS-11852
- https://research.checkpoint.com/2025/cve-2025-24054-ntlm-exploit-in-the-wild
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52465.json
- https://github.com/geoserver/geoserver/security/advisories/GHSA-7qmg-grcp-qf25
- https://nvd.nist.gov/vuln/detail/CVE-2025-52465
- https://github.com/geoserver/geoserver/pull/8584
