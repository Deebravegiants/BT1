# [H] WPS Server Side Request Forgery vulnerability

## Summary
Severity: High
Advisory: GHSA-5pr3-m5hm-9956
CVE: CVE-2023-43795
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2023-10-24
Source: https://github.com/advisories/GHSA-5pr3-m5hm-9956
Type: github-advisory

## Affected
- Maven: `org.geoserver.extension:gs-wps-core` — affected >=0 <2.22.5
- Maven: `org.geoserver.extension:gs-wps-core` — affected >=2.23.0 <2.23.2

## Details
### Summary

The OGC Web Processing Service (WPS) specification is designed to process information from any server using GET and POST requests.

This presents the opportunity for Server Side Request Forgery.

## Details

This vulnerability requires:

* The WPS extension to be installed
* The WPS security setting "Disable complex inputs" to be unselected
* Security URL checks to be disabled

### Impact

This vulnerability presents the opportunity for Server Side Request Forgery.

### Mitigation

The ability to reference an external URL location is defined by the WPS standard Execute operation. This operations is defined by an Industry and International standard and cannot be redefined by the GeoServer application in isolation.

To disable complex remote inputs on GeoServer 2.20.5 and GeoServer 2.21.0:

1.  Navigate to **Security > WPS Security** page
2. Locate **Complex Inputs** heading
3. Select the check box for **Disable loading complex inputs from remote references**

### Resolution

To allow processing of complex inputs safely in GeoServer 2.22.5 and GeoServer 2.23.2:

1. Navigate to **Security > URL Checks**
2. Enable **URL Checks** are enabled setting
3. Check the user manual for [examples](https://docs.geoserver.org/latest/en/user/security/urlchecks.html#example-regex-patterns) of how to trust specific locations for your external services.

Processing of complex inputs safely is on by default in GeoServer 2.24.0.

### References

* [Complex Inputs](https://docs.geoserver.org/stable/en/user/services/wps/security.html#complex-inputs)
* [URL Checks](https://docs.geoserver.org/latest/en/user/security/urlchecks.html)

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-5pr3-m5hm-9956
- https://nvd.nist.gov/vuln/detail/CVE-2023-43795
- https://docs.geoserver.org/latest/en/user/security/urlchecks.html
- https://docs.geoserver.org/stable/en/user/services/wps/security.html#complex-inputs
- https://github.com/geoserver/geoserver
