# [M] Coverage REST API Server Side Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-r4hf-r8gj-jgw2
CVE: CVE-2024-40625
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2025-06-10
Source: https://github.com/advisories/GHSA-r4hf-r8gj-jgw2
Type: github-advisory

## Affected
- Maven: `org.geoserver:gs-rest` — affected >=0 <2.26.0
- Maven: `org.geoserver.web:gs-web-app` — affected >=0 <2.26.0

## Details
### Summary

The Coverage rest api `/workspaces/{workspaceName}/coveragestores/{storeName}/{method}.{format}` allow to upload file with a specified url (with {method} equals 'url') with no restrict.

### Details

The Coverage rest api `/workspaces/{workspaceName}/coveragestores/{storeName}/{method}.{format}` allow to upload file with a specified url (with {method} equals 'url'). But this url has not been check with [URL Checks feature](https://docs.geoserver.org/latest/en/user/security/urlchecks.html#url-checks).

For example, should add the code below to check fileURL:

```java
URLCheckers.confirm(fileURL)
```

The vulnerable code was [RESTUtils.java](https://github.com/geoserver/geoserver/blob/main/src/rest/src/main/java/org/geoserver/rest/util/RESTUtils.java#L176)

### Impact

This vulnerability presents the opportunity for Server Side Request Forgery.

### References

- https://osgeo-org.atlassian.net/browse/GEOS-11468
- https://osgeo-org.atlassian.net/browse/GEOS-11717

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-r4hf-r8gj-jgw2
- https://nvd.nist.gov/vuln/detail/CVE-2024-40625
- https://github.com/geoserver/geoserver
- https://osgeo-org.atlassian.net/browse/GEOS-11468
- https://osgeo-org.atlassian.net/browse/GEOS-11717
