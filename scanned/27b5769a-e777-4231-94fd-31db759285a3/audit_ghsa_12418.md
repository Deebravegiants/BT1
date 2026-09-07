# [C] Improper JWT Signature Validation in SAP Security Services Library 

## Summary
Severity: Critical
Advisory: GHSA-59c9-pxq8-9c73
CVE: CVE-2023-50422
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-59c9-pxq8-9c73
Type: github-advisory

## Affected
- Maven: `com.sap.cloud.security:java-security` — affected >=0 <2.17.0
- Maven: `com.sap.cloud.security:java-security` — affected >=3.0.0 <3.3.0
- Maven: `com.sap.cloud.security:spring-security` — affected >=0 <2.17.0
- Maven: `com.sap.cloud.security:spring-security` — affected >=3.0.0 <3.3.0
- Maven: `com.sap.cloud.security.xsuaa:spring-xsuaa` — affected >=0 <2.17.0
- Maven: `com.sap.cloud.security.xsuaa:spring-xsuaa` — affected >=3.0.0 <3.3.0

## Details
### Impact
SAP BTP Security Services Integration Library ([Java] cloud-security-services-integration-library) allows under certain conditions an escalation of privileges. On successful exploitation, an unauthenticated attacker can obtain arbitrary permissions within the application.

### Patches
Upgrade to patched version >= 2.17.0 or >= 3.3.0 
We always recommend to upgrade to the latest released version.

### Workarounds
No workarounds

### References
https://www.cve.org/CVERecord?id=CVE-2023-50422

## References
- https://github.com/SAP/cloud-security-services-integration-library/security/advisories/GHSA-59c9-pxq8-9c73
- https://nvd.nist.gov/vuln/detail/CVE-2023-50422
- https://github.com/SAP/cloud-security-services-integration-library/commit/4b3e42ab23df6418243b29908b1a2582818d9360
- https://github.com/SAP/cloud-security-services-integration-library/commit/7ce9601979c30ae269a1cbaf7cf33486d10736f1
- https://blogs.sap.com/2023/12/12/unveiling-critical-security-updates-sap-btp-security-note-3411067
- https://en.wikipedia.org/wiki/JSON_Web_Token
- https://github.com/SAP/cloud-security-services-integration-library
- https://me.sap.com/notes/3411067
- https://me.sap.com/notes/3413475
- https://mvnrepository.com/artifact/com.sap.cloud.security.xsuaa/spring-xsuaa
- https://mvnrepository.com/artifact/com.sap.cloud.security/java-security
- https://mvnrepository.com/artifact/com.sap.cloud.security/spring-security
- https://www.sap.com/documents/2022/02/fa865ea4-167e-0010-bca6-c68f7e60039b.html
