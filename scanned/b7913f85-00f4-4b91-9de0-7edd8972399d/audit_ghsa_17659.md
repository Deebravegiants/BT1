# [C] GeoTools has XML External Entity (XXE) Processing Vulnerability in XSD schema handling

## Summary
Severity: Critical
Advisory: GHSA-826p-4gcg-35vw
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2025-06-09
Source: https://github.com/advisories/GHSA-826p-4gcg-35vw
Type: github-advisory

## Affected
- Maven: `org.geotools:gt-xsd-core` — affected >=33.0 <33.1
- Maven: `org.geotools:gt-xsd-core` — affected >=32.0 <32.3
- Maven: `org.geotools:gt-xsd-core` — affected >=29.0 <31.7
- Maven: `org.geotools:gt-wfs-ng` — affected >=33.0 <33.1
- Maven: `org.geotools:gt-wfs-ng` — affected >=32.0 <32.3
- Maven: `org.geotools:gt-wfs-ng` — affected >=29.0 <31.7
- Maven: `org.geotools:gt-xsd-core` — affected >=0 <28.6.1
- Maven: `org.geotools:gt-wfs-ng` — affected >=0 <28.6.1

## Details
### Summary

GeoTools Schema class use of Eclipse XSD library to represent schema data structure is vulnerable to XML External Entity (XXE) exploit.

### Impact

This impacts whoever exposes XML processing with ``gt-xsd-core`` involved in parsing, when the documents carry a reference to an external XML schema. The ``gt-xsd-core`` Schemas class is not using the EntityResolver provided by the ParserHandler (if any was configured).

This also impacts users of ``gt-wfs-ng`` DataStore where the ENTITY_RESOLVER connection parameter was not being used as intended.

### Resolution

GeoTools API change allows EntityResolver to be supplied to the following methods:

```java
Schemas.parse( location, locators, resolvers, uriHandlers, entityResolver);
Schemas.findSchemas(Configuration configuration, EntityResolver entityResolver);
```

With this API change the `gt-wfs-ng` WFS DataStore ENTITY_RESOLVER parameter is now used.

### Reference

* [GHSA-jj54-8f66-c5pc](https://github.com/geoserver/geoserver/security/advisories/GHSA-jj54-8f66-c5pc): Describes the impact of the ``gt-xsd-core`` vulnerability on the GeoServer WFS protocol, resulting in both Service Side Request Forgery (SSRF) and Out-of-Band (OOB) data exfiltration of local files.

* [GHSA-2p76-gc46-5fvc](https://github.com/geonetwork/core-geonetwork/security/advisories/GHSA-2p76-gc46-5fvc): Describes the impact of the ``gt-wfs-ng`` and ``gt-xsd-core`` vulnerability on the GeoNetwork WFS Index functionality.

## References
- https://github.com/geonetwork/core-geonetwork/security/advisories/GHSA-2p76-gc46-5fvc
- https://github.com/geoserver/geoserver/security/advisories/GHSA-jj54-8f66-c5pc
- https://github.com/geotools/geotools/security/advisories/GHSA-826p-4gcg-35vw
- https://github.com/geotools/geotools
