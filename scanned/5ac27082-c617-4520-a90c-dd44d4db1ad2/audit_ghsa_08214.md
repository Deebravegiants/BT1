# [C] Goobi viewer - Core: Unauthenticated Solr Streaming Expression Proxy

## Summary
Severity: Critical
Advisory: GHSA-2rgp-f66f-4499
CVE: CVE-2026-45083
CWE: CWE-306
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-2rgp-f66f-4499
Type: github-advisory

## Affected
- Maven: `io.goobi.viewer:viewer-core` — affected >=4.8.0

## Details
### Summary

The Goobi viewer REST endpoint `POST /api/v1/index/stream` accepted an arbitrary Solr streaming
expression from unauthenticated network clients and forwarded it to the backend Solr server without restriction.
An attacker could read the complete Solr index and, in default Solr deployments, also modify or delete indexed records.

The API endpoint has now been removed.

### Impact

- **Complete Solr index read without authentication.**
  All documents indexed by the viewer  including those protected by access conditions such as moving walls, licence requirements or IP restrictions - can be read in full.

- **Index data modification.**
  `update()` streaming expressions overwrite indexed field values. An attacker can alter metadata, change `ACCESSCONDITION` values, or corrupt document structure.

- **Index data deletion.**
  `delete()` streaming expressions permanently remove documents. A single expression can delete the entire collection, requiring a full re-index to recover.

### Patches

The endpoint was removed in 326980f24c

### Workarounds

Until an update can be deployed, the endpoint should be blocked by a reverse proxy or in the tomcat configuration.

For Apache httpd the following block can be used in the vhost configuration:

```
<LocationMatch ^.*api/v[12]/index/stream.*$>
    Require all denied
</LocationMatch>
```

Alternatively the following security constraint can be added in tomcat via the relevant web.xml:
```
<security-constraint>
      <web-resource-collection>
        <web-resource-name>blocked endpoint</web-resource-name>
        <url-pattern>/api/v1/index/stream</url-pattern>
        <url-pattern>/api/v1/index/stream/*</url-pattern>
      </web-resource-collection>
      <auth-constraint/>
</security-constraint>
```

### References

- Fix commit: 326980f24c
- Introducing commit: 6bfb1cbd42
- [Solr Streaming Expressions reference](https://solr.apache.org/guide/solr/latest/query-guide/streaming-expressions.html)


### Contact

If you have any questions or comments about this advisory:

- Email us at [support@intranda.com](mailto:support@intranda.com)

## References
- https://github.com/intranda/goobi-viewer-core/security/advisories/GHSA-2rgp-f66f-4499
- https://nvd.nist.gov/vuln/detail/CVE-2026-45083
- https://github.com/intranda/goobi-viewer-core/commit/326980f24ce1e7cfabf658dd5f615934ca68ebbd
- https://github.com/intranda/goobi-viewer-core/commit/6bfb1cbd4250b0b347e84a80f38e8bf46acac705
- https://github.com/intranda/goobi-viewer-core
- https://github.com/intranda/goobi-viewer-core/releases/tag/v26.04.1
