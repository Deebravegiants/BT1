# [H] Geoserver for GeoNode sensitive information leak

## Summary
Severity: High
Advisory: CVE-2023-28442
Aliases: GHSA-87mh-vw7c-5v6w
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-03-23
Source: https://osv.dev/vulnerability/CVE-2023-28442
Type: osv

## Details
GeoNode is an open source platform that facilitates the creation, sharing, and collaborative use of geospatial data. Prior to versions 2.20.6, 2.19.6, and 2.18.7, anonymous users can obtain sensitive information about GeoNode configurations from the response of the `/geoserver/rest/about/status` Geoserver REST API endpoint. The Geoserver endpoint is secured by default, but the configuration of Geoserver for GeoNode opens a list of REST endpoints to support some of its public-facing services. The vulnerability impacts both GeoNode 3 and GeoNode 4 instances.

Geoserver security configuration is provided by `geoserver-geonode-ext`. A patch for 2.20.7 has been released which blocks access to the affected endpoint. The patch has been backported to branches 2.20.6, 2.19.7, 2.19.6, and 2.18.7. All the published artifacts and Docker images have been updated accordingly. A more advanced patch has been applied to the master and development versions, which require some changes to GeoNode code. They will be available with the next 4.1.0 release. The patched configuration only has an effect on new deployments. For existing setups, the patch must be applied manually inside the Geoserver data directory. The patched file must replace the existing `<geoserver_datadir>/security/rest.properties` file.

## References
- https://github.com/GeoNode/geoserver-geonode-ext/blob/2.20.7/data/security/rest.properties
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28442.json
- https://github.com/GeoNode/geonode/security/advisories/GHSA-87mh-vw7c-5v6w
- https://nvd.nist.gov/vuln/detail/CVE-2023-28442
- https://github.com/GeoNode/geoserver-geonode-ext/commit/f44cb074d8361c0f4e625013675bdd7bd8203df6
