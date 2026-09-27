# [H] GeoServer log file path traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-8g7v-vjrc-x4g5
CVE: CVE-2023-41877
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-20
Source: https://github.com/advisories/GHSA-8g7v-vjrc-x4g5
Type: github-advisory

## Affected
- Maven: `org.geoserver:gs-main` — affected >=0

## Details
### Impact

This vulnerability requires GeoServer Administrator with access to the admin console  to misconfigured the **Global Settings** for **log file location** to an arbitrary location.

This can be used to read files via the admin console **GeoServer Logs** page. It is also possible to leverage RCE or cause denial of service by overwriting key GeoServer files.

### Patches

This issue has been addressed in GeoServer 3.0.0:
* The Global Settings page can no longer be used to specify log file location
* The application parameter ``GEOSERVER_LOG_LOCATION`` mechanism (outlined below) is now the only approach available to customize the log file location.

### Workarounds

A system administrator responsible for running GeoServer can define  the ``GEOSERVER_LOG_FILE`` parameter, preventing the global setting provided from being used.

The ``GEOSERVER_LOG_LOCATION`` parameter can be set as system property, environment variable, or servlet context parameter.

Environmental variable:
```bash
export GEOSERVER_LOG_LOCATION=/var/opt/geoserver/logs
```

System property:
```bash
-DGEOSERVER_LOG_LOCATION=/var/opt/geoserver/logs
```

Web application ``WEB-INF/web.xml``:
```xml
  <context-param>
    <param-name> GEOSERVER_LOG_LOCATION </param-name>
    <param-value>/var/opt/geoserver/logs</param-value>
  </context-param>
```

Tomcat **conf/Catalina/localhost/geoserver.xml**:
```xml
<Context>
  <Parameter name="GEOSERVER_LOG_LOCATION"
             value="/var/opt/geoserver/logs" override="false"/>
</Context>
```

### References

* [Upgrading GeoServer 3](https://docs.geoserver.org/main/en/user/installation/upgrade3/#log-location-configuration)
* [Log location](https://docs.geoserver.org/latest/en/user/configuration/globalsettings/#logging-settings) (User Manual)

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-8g7v-vjrc-x4g5
- https://nvd.nist.gov/vuln/detail/CVE-2023-41877
- https://docs.geoserver.org/latest/en/user/configuration/globalsettings.html#log-location
- https://github.com/geoserver/geoserver
