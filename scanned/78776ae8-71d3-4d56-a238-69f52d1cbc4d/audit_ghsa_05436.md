# [M] Apache SIS has Improper Restriction of XML External Entity Reference vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jqmr-2pg9-vfx7
CVE: CVE-2025-68280
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-jqmr-2pg9-vfx7
Type: github-advisory

## Affected
- Maven: `org.apache.sis.core:sis-metadata` — affected >=0.4 <1.6

## Details
Improper Restriction of XML External Entity Reference vulnerability in Apache SIS.



It is possible to write XML files in such a way that, when parsed by Apache SIS, an XML file reveals to the attacker the content of a local file on the server running Apache SIS. This vulnerability impacts the following SIS services:




  *  Reading of GeoTIFF files having the GEO_METADATA tag defined by the Defense Geospatial Information Working Group (DGIWG).

  *  Parsing of ISO 19115 metadata in XML format.

  *  Parsing of Coordinate Reference Systems defined in the GML format.

  *  Parsing of files in GPS Exchange Format (GPX).





This issue affects Apache SIS from versions 0.4 through 1.5 inclusive. Users are recommended to upgrade to version 1.6, which will fix the issue. In the meantime, the security vulnerability can be avoided by launching Java with the javax.xml.accessExternalDTD system property sets to a comma-separated list of authorized protocols. For example:



java -Djavax.xml.accessExternalDTD="" ...

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-68280
- https://github.com/apache/sis
- https://lists.apache.org/thread/s4ggy3zbtrrn93glgo2vn52lgcxk4bp4
- http://www.openwall.com/lists/oss-security/2026/01/05/11
- http://www.openwall.com/lists/oss-security/2026/01/05/7
