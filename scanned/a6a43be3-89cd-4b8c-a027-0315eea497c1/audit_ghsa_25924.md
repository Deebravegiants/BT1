# [C] Improper Restriction of XML External Entity Reference in soa-model

## Summary
Severity: Critical
Advisory: GHSA-pv39-qp28-4mgh
CVE: CVE-2021-43090
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-26
Source: https://github.com/advisories/GHSA-pv39-qp28-4mgh
Type: github-advisory

## Affected
- Maven: `com.predic8:soa-model-parent` — affected >=0 <1.6.4
- Maven: `com.predic8:soa-model-core` — affected >=0 <1.6.4

## Details
Soa-model is a toolkit and Java API for WSDL, WADL and XML Schema. An XML External Entity (XXE) vulnerability exists in versions of soa-model prior to 1.6.4 in the WSDLParser function. This issue has been fixed in version 1.6.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43090
- https://github.com/membrane/soa-model/issues/281
- https://github.com/membrane/soa-model/commit/19de16902468e7963cc4dc6b544574bc1ea3f251
- https://github.com/membrane/soa-model/commit/3aa295f155f621d5ea661cb9a0604013fc8fd8ff
- https://github.com/membrane/soa-model
- https://github.com/membrane/soa-model/releases/tag/v1.6.4
