# [H] Classpath resource disclosure in GWC Web Resource API on Windows / Tomcat

## Summary
Severity: High
Advisory: GHSA-jhqx-5v5g-mpf3
CVE: CVE-2024-24749
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-01
Source: https://github.com/advisories/GHSA-jhqx-5v5g-mpf3
Type: github-advisory

## Affected
- Maven: `org.geoserver.web:gs-web-app` — affected >=0 <2.23.5
- Maven: `org.geoserver.web:gs-web-app` — affected >=2.24.0 <2.24.3
- Maven: `org.geoserver:gs-gwc` — affected >=0 <2.23.5
- Maven: `org.geoserver:gs-gwc` — affected >=2.24.0 <2.24.3

## Details
### Impact

If GeoServer is deployed in the Windows operating system using an Apache Tomcat web application server, it is possible to bypass existing input validation in the GeoWebCache ByteStreamController class and read arbitrary classpath resources with specific file name extensions.

If GeoServer is also deployed as a web archive using the data directory embedded in the geoserver.war file (rather than an external data directory), it will likely be possible to read specific resources to gain administrator privileges.  However, it is very unlikely that production environments will be using the embedded data directory since, depending on how GeoServer is deployed, it will be erased and re-installed (which would also reset to the default password) either every time the server restarts or every time a new GeoServer WAR is installed and is therefore difficult to maintain. An external data directory will always be used if GeoServer is running in standalone mode (via an installer or a binary).

### Patches

https://github.com/GeoWebCache/geowebcache/pull/1211

### Workarounds

Change environment:

* Change from Windows operating system. This vulnerability depends on Windows file paths so Linux and Mac OS are not vulnerable.
* Change from Apache Tomcat application server. Jetty and WildFly are confirmed to not be vulnerable. Other application servers have not been tested and may be vulnerable.

Disable anonymous access to the embeded GeoWebCache administration and status pages:

1. Navigate to **Security > Authentication** Page
2. Locate **Filter Chains** heading
3. Select the ``web`` filter filter chain (ant pattern ``/web/**,/gwc/rest/web/**,/``)
4. Remove ``,/gwc/rest/web/**`` from the pattern (so that ``/web/**,/`` is left).
5. Save the changes

### References

* CVE-Pending

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-jhqx-5v5g-mpf3
- https://nvd.nist.gov/vuln/detail/CVE-2024-24749
- https://github.com/GeoWebCache/geowebcache/pull/1211
- https://github.com/GeoWebCache/geowebcache/commit/c7f76bd8a1d67c3b986146e7a5e0b14dd64a8fef
- https://github.com/geoserver/geoserver
- http://seclists.org/fulldisclosure/2024/Feb/13
