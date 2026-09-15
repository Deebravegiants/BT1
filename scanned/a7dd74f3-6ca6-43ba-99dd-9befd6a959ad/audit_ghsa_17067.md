# [M] SQL injection in Folio Spring Module Core

## Summary
Severity: Medium
Advisory: GHSA-4h5h-p23f-hjqf
CVE: CVE-2022-4963
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-03-21
Source: https://github.com/advisories/GHSA-4h5h-p23f-hjqf
Type: github-advisory

## Affected
- Maven: `org.folio:spring-module-core` — affected >=0 <2.0.0

## Details
A vulnerability was found in Folio Spring Module Core before 2.0.0. Affected by this issue is the function dropSchema of the file tenant/src/main/java/org/folio/spring/tenant/hibernate/HibernateSchemaService.java of the component Schema Name Handler. The manipulation leads to sql injection. Upgrading to version 2.0.0 is able to address this issue. The name of the patch is d374a5f77e6b58e36f0e0e4419be18b95edcd7ff. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-257516.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4963
- https://github.com/folio-org/spring-module-core/pull/39
- https://github.com/folio-org/spring-module-core/commit/d374a5f77e6b58e36f0e0e4419be18b95edcd7ff
- https://github.com/folio-org/spring-module-core/releases/tag/v2.0.0
- https://vuldb.com/?ctiid.257516
- https://vuldb.com/?id.257516
