# [C] bonita-connector-webservice XML External Entity vulnerability

## Summary
Severity: Critical
Advisory: GHSA-wg99-5vrx-j2gg
CVE: CVE-2020-36640
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-05
Source: https://github.com/advisories/GHSA-wg99-5vrx-j2gg
Type: github-advisory

## Affected
- Maven: `org.bonitasoft.connectors:bonita-connector-webservice` — affected >=0 <1.3.1

## Details
A vulnerability, which was classified as problematic, was found in bonitasoft bonita-connector-webservice up to 1.3.0. This affects the function `TransformerConfigurationException` of the file `src/main/java/org/bonitasoft/connectors/ws/SecureWSConnector.java`. The manipulation leads to xml external entity reference. Upgrading to version 1.3.1 can address this issue. The name of the patch is a12ad691c05af19e9061d7949b6b828ce48815d5. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-217443.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36640
- https://github.com/bonitasoft/bonita-connector-webservice/pull/17
- https://github.com/bonitasoft/bonita-connector-webservice/commit/a12ad691c05af19e9061d7949b6b828ce48815d5
- https://github.com/bonitasoft/bonita-connector-webservice
- https://github.com/bonitasoft/bonita-connector-webservice/releases/tag/1.3.1
- https://vuldb.com/?ctiid.217443
- https://vuldb.com/?id.217443
