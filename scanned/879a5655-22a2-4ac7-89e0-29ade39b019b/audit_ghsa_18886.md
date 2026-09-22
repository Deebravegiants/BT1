# [H] GeoServer is vulnerable to Unauthenticated XML External Entities (XXE) attack via WMS GetMap feature

## Summary
Severity: High
Advisory: GHSA-fjf5-xgmq-5525
CVE: CVE-2025-58360
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2025-11-25
Source: https://github.com/advisories/GHSA-fjf5-xgmq-5525
Type: github-advisory

## Affected
- Maven: `org.geoserver.web:gs-web-app` — affected >=2.26.0 <2.26.2
- Maven: `org.geoserver:gs-wms` — affected >=2.26.0 <2.26.2
- Maven: `org.geoserver.web:gs-web-app` — affected >=0 <2.25.6
- Maven: `org.geoserver:gs-wms` — affected >=0 <2.25.6

## Details
## Description

An XML External Entity (XXE) vulnerability was identified. The application accepts XML input through a specific endpoint ``/geoserver/wms`` operation ``GetMap``. However, this input is not sufficiently sanitized or restricted, allowing an attacker to define external entities within the XML request.

An XML External Entity attack is a type of attack that occurs when XML input containing a reference to an external entity is processed by a weakly configured XML parser. This attack may lead to the disclosure of confidential data, denial of service, port scanning from the perspective of the machine where the parser is located, and other system impacts.

By exploiting this vulnerability, an attacker can:
- Read arbitrary files from the server's file system.
- Conduct Server-Side Request Forgery (SSRF) to interact with internal systems.
- Execute Denial of Service (DoS) attacks by exhausting resources.

## Resolution

Update to GeoServer 2.25.6, GeoServer 2.26.3, or GeoServer 2.27.0.

## Impact

The XXE vulnerability can be used to retrieve arbitrary files from the server's file system.

## Reference

* https://osgeo-org.atlassian.net/browse/GEOS-11682
* XBOW-024-081

## Disclaimer

This vulnerability was detected using **[XBOW](https://xbow.com/)**, a system that autonomously finds and exploits potential security vulnerabilities. The finding has been thoroughly reviewed and validated by a security researcher before submission. While XBOW is intended to work autonomously, during its development human experts ensure the accuracy and relevance of its reports.

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-fjf5-xgmq-5525
- https://nvd.nist.gov/vuln/detail/CVE-2025-58360
- https://github.com/geoserver/geoserver
- https://osgeo-org.atlassian.net/browse/GEOS-11682
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-58360
