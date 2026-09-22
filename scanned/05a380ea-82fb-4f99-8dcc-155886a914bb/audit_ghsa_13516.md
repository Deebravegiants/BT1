# [M] Unsecured WMS dynamic styling sld=<url> parameter affords blind unauthenticated SSRF

## Summary
Severity: Medium
Advisory: GHSA-cqpc-x2c6-2gmf
CVE: CVE-2023-41339
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-10-24
Source: https://github.com/advisories/GHSA-cqpc-x2c6-2gmf
Type: github-advisory

## Affected
- Maven: `org.geoserver:gs-wms` — affected >=0 <2.22.5
- Maven: `org.geoserver:gs-wms` — affected >=2.23.0 <2.23.2
- Maven: `org.geoserver.web:gs-web-app` — affected >=0 <2.22.5
- Maven: `org.geoserver.web:gs-web-app` — affected >=2.23.0 <2.23.2

## Details
### Summary

The WMS specification defines an ``sld=<url>`` parameter for GetMap, GetLegendGraphic and GetFeatureInfo operations for user supplied "dynamic styling".  Enabling the use of dynamic styles, without also configuring URL checks, provides the opportunity for Service Side Request Forgery.
 
It is possible to use this for "Blind SSRF" on the WMS endpoint to steal NetNTLMv2 hashes via file requests to malicious servers.

### Details

This vulnerability requires:

* WMS Settings dynamic styling being enabled
* Security URL checks to be disabled, or to be enabled and allowing ``file:\\*`` access

### Impact

This vulnerability can be used to steal user NetNTLMv2 hashes which could be relayed or cracked externally to gain further access.

### Mitigation

The ability to reference an external URL location is defined by the WMS standard GetMap, GetFeatureInfo and GetLegendGraphic operations. These operations are defined by an Industry and International standard and cannot be redefined by the GeoServer application in isolation.

To disable dynamic styling on GeoServer 2.10.3 and GeoServer 2.11.1:

1. Navigate to **Services > WMS Settings** page
2. Locate **Dynamic styling** heading
3. Select the **Disable usage of SLD and SLD_BODY parameters in GET requests and user styles in POST** checkbox.

### Resolution

To allow dynamic styling safely on GeoServer 2.22.5 and GeoServer 2.23.2:

1. Navigate to **Security > URL Checks**
2. Enable **URL Checks are enabled** setting
3. Check the user manual for [examples](https://docs.geoserver.org/latest/en/user/security/urlchecks.html#example-regex-patterns) of how to trust specific locations:
   ``^https://styles\.server\.net/cartography/.*$``
4. Enable dynamic styling on the **Services > WMS Settings** page, deselect the **Disable usage of SLD and SLD_BODY parameters in GET requests and user styles in POST** checkbox.

Use of dynamic styling safely is on by default in GeoServer 2.24.0.

### References

* [Disabling usage of dynamic styling in GetMap, GetFeatureInfo and GetLegendGraphic requests](https://docs.geoserver.org/latest/en/user/services/wms/webadmin.html#disabling-usage-of-dynamic-styling-in-getmap-getfeatureinfo-and-getlegendgraphic-requests)
* [URL Checks](https://docs.geoserver.org/latest/en/user/security/urlchecks.html)

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-cqpc-x2c6-2gmf
- https://nvd.nist.gov/vuln/detail/CVE-2023-41339
- https://github.com/geoserver/geoserver
- https://github.com/geoserver/geoserver/releases/tag/2.22.5
- https://github.com/geoserver/geoserver/releases/tag/2.23.2
