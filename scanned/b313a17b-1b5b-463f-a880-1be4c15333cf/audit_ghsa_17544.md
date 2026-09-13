# [H] GeoServer Vulnerable to Unauthenticated SSRF via TestWfsPost

## Summary
Severity: High
Advisory: GHSA-5gw5-jccf-6hxw
CVE: CVE-2024-29198
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-10
Source: https://github.com/advisories/GHSA-5gw5-jccf-6hxw
Type: github-advisory

## Affected
- Maven: `org.geoserver:gs-wfs` — affected >=2.0.0 <2.24.4
- Maven: `org.geoserver.web:gs-app` — affected >=2.0.0 <2.24.4
- Maven: `org.geoserver:gs-wfs` — affected >=2.25.0 <2.25.2
- Maven: `org.geoserver.web:gs-app` — affected >=2.25.0 <2.25.2

## Details
### Summary

It possible to achieve Service Side Request Forgery (SSRF) via the Demo request endpoint if Proxy Base URL has not been set.

### Details

A unauthenticated user can supply a request that will be issued by the server. This can be used to enumerate internal networks and also in the case of cloud instances can be used to obtain sensitive data.

### Mitigation

1. When using GeoServer with a proxy, manage the proxy base value as a system administrator, use the application property ``PROXY_BASE_URL`` to provide a non-empty value that cannot be overridden by the user interface or incoming request.

2. When using GeoServer directly without a proxy, block all access to TestWfsPost by editing the web.xml file. Adding this block right before the end:

   ```xml
      <security-constraint>
           <web-resource-collection>
               <web-resource-name>BlockDemoRequests</web-resource-name>
               <url-pattern>/TestWfsPost/*</url-pattern>
           </web-resource-collection>
           <auth-constraint>
               <role-name>BLOCKED</role-name>
           </auth-constraint>
       </security-constraint>
   ```

### Resolution

Upgrading to GeoServer 2.24.4, or 2.25.2, removes the ``TestWfsPost`` servlet resolving this issue.

The demo request page functionality is now implemented directly in the browser.

### Reference

- https://osgeo-org.atlassian.net/browse/GEOS-11794
- https://osgeo-org.atlassian.net/browse/GEOS-11390
- https://nvd.nist.gov/vuln/detail/CVE-2021-40822

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-5gw5-jccf-6hxw
- https://nvd.nist.gov/vuln/detail/CVE-2021-40822
- https://nvd.nist.gov/vuln/detail/CVE-2024-29198
- https://github.com/geoserver/geoserver
- https://osgeo-org.atlassian.net/browse/GEOS-11390
- https://osgeo-org.atlassian.net/browse/GEOS-11794
