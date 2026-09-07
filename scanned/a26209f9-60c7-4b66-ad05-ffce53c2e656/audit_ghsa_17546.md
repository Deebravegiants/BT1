# [H] GeoServer vulnerable to SSRF in TestWfsPost for specific targets, e.g. PHP + Nginx

## Summary
Severity: High
Advisory: GHSA-68cf-j696-wvv9
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-10
Source: https://github.com/advisories/GHSA-68cf-j696-wvv9
Type: github-advisory

## Affected
- Maven: `org.geoserver:gs-wfs` — affected >=1.0.0 <2.24.4
- Maven: `org.geoserver:gs-wfs` — affected >=2.25.0 <2.25.2

## Details
### Summary

Missing checks allow for SSRF to specific targets using the TestWfsPost enpoint. 

### Mitigation

To manage the proxy base value as a system administrator, use the parameter ``PROXY_BASE_URL`` to provide a non-empty value that cannot be overridden by the user interface or incoming request.[thomsmith](https://github.com/thomsmith).

### Resolution

The TestWfsPost has been replaced in GeoServer 2.25.2 and GeoServer 2.24.4 with a JavaScript [Demo Requests](https://docs.geoserver.org/latest/en/user/configuration/demos/index.html#demo-requests) page to test OGC Web Services.

### References

* [CVE-2024-29198](https://github.com/geoserver/geoserver/security/advisories/GHSA-5gw5-jccf-6hxw) Unauthenticated SSRF via TestWfsPost

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-5gw5-jccf-6hxw
- https://github.com/geoserver/geoserver/security/advisories/GHSA-68cf-j696-wvv9
- https://github.com/geoserver/geoserver
