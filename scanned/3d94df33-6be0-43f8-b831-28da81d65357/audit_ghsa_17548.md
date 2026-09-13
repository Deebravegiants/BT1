# [H] [XBOW-025-068] XML External Entity (XXE) Processing Vulnerability in GeoServer WFS Service

## Summary
Severity: High
Advisory: GHSA-jj54-8f66-c5pc
CVE: CVE-2025-30220
CWE: CWE-611, CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2025-06-10
Source: https://github.com/advisories/GHSA-jj54-8f66-c5pc
Type: github-advisory

## Affected
- Maven: `org.geoserver.web:gs-web-app` — affected >=2.27.0 <2.27.1
- Maven: `org.geoserver:gs-wfs` — affected >=2.27.0 <2.27.1
- Maven: `org.geoserver.web:gs-web-app` — affected >=2.26.0 <2.26.3
- Maven: `org.geoserver:gs-wfs` — affected >=2.26.0 <2.26.3
- Maven: `org.geoserver.web:gs-web-app` — affected >=0 <2.25.7
- Maven: `org.geoserver:gs-wfs` — affected >=0 <2.25.7

## Details
## Summary

GeoServer Web Feature Service (WFS) web service was found to be vulnerable to GeoTools CVE-2025-30220 XML External Entity (XXE) processing attack.

It is possible to trigger the parsing of external DTDs and entities, bypassing standard entity resolvers.  This allows for Out-of-Band (OOB) data exfiltration of local files accessible by the GeoServer process, and Service Side Request Forgery (SSRF).

## Details

While direct entity resolution is managed by application property ENTITY_RESOLUTION_ALLOWLIST for XML Parsing, this restriction was not being used by the GeoTools library when building an in-memory XSD Library Schema representation.

This bypasses GeoServer's AllowListEntityResolver enabling XXE attacks.

## PoC

No public PoC is provided but this vulnerability has been confirmed to be exploitable through WFS service.

## Impact

* Information Disclosure: 

  This vulnerability allows unauthenticated attackers to read arbitrary files from the server's filesystem that are accessible to the GeoServer process.
  
  This can lead to exposure of sensitive information including configuration files, credentials, and system files. The attack can be performed remotely without authentication, making it particularly severe.

* Server-Side Request Forgery (SSRF) 
  
  The mechanism inherently allows forcing GeoServer to make HTTP requests to arbitrary URLs, enabling SSRF attacks against internal network resources 

## References

* [CVE-2025-30220](https://github.com/geotools/geotools/security/advisories/GHSA-826p-4gcg-35vw) XML External Entity (XXE) Processing Vulnerability in XSD schema handling
* [External Entities Resolution](https://docs.geoserver.org/latest/en/user/production/config.html#production-config-external-entities) (GeoServer User Manual)

## Acknowledgements

This vulnerability was initially reported via an automated tool described below. Subsequently a duplicate report via @YacineF, and their patience working with the GeoServer project, was instrumental finding in escalating this issue and determining a resolution.

### XBOW-025-068 Disclaimer

This vulnerability was detected using **[XBOW](https://xbow.com/)**, a system that autonomously finds and exploits potential security vulnerabilities. The finding has been thoroughly reviewed and validated by a security researcher before submission. While XBOW is intended to work autonomously, during its development human experts ensure the accuracy and relevance of its reports.

## References
- https://github.com/geonetwork/core-geonetwork/security/advisories/GHSA-2p76-gc46-5fvc
- https://github.com/geoserver/geoserver/security/advisories/GHSA-jj54-8f66-c5pc
- https://github.com/geotools/geotools/security/advisories/GHSA-826p-4gcg-35vw
- https://nvd.nist.gov/vuln/detail/CVE-2025-30220
- https://github.com/geonetwork/core-geonetwork/pull/8757
- https://github.com/geonetwork/core-geonetwork/pull/8803
- https://github.com/geonetwork/core-geonetwork/pull/8812
- https://docs.geoserver.org/latest/en/user/production/config.html#production-config-external-entities
- https://github.com/geoserver/geoserver
