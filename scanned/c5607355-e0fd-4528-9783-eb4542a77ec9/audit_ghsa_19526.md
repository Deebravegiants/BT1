# [H] generator-jhipster-entity-audit vulnerable to Unsafe Reflection when having Javers selected as Entity Audit Framework

## Summary
Severity: High
Advisory: GHSA-7rmp-3g9f-cvq8
CVE: CVE-2025-31119
CWE: CWE-470
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-04
Source: https://github.com/advisories/GHSA-7rmp-3g9f-cvq8
Type: github-advisory

## Affected
- npm: `generator-jhipster-entity-audit` — affected >=0 <5.9.1

## Details
### Summary
CWE-470 (Use of Externally-Controlled Input to Select Classes or Code ('Unsafe Reflection') when having Javers selected as Entity Audit Framework

### Details
In the following two occurences, user input directly leads to class loading without checking against e.g. a whitelist of allowed classes. This is also known as CWE-470
https://github.com/jhipster/generator-jhipster-entity-audit/blob/e21e83135d10c77d92203c89cb0b0063914e8fe0/generators/spring-boot-javers/templates/src/main/java/_package_/web/rest/JaversEntityAuditResource.java.ejs#L88
https://github.com/jhipster/generator-jhipster-entity-audit/blob/e21e83135d10c77d92203c89cb0b0063914e8fe0/generators/spring-boot-javers/templates/src/main/java/_package_/web/rest/JaversEntityAuditResource.java.ejs#L124

So, if an attacker manages to place some malicious classes into the classpath and also has access to these REST interface for calling the mentioned REST endpoints, using these lines of code can lead to unintended remote code execution.

### PoC

1. Place an arbitrary class with the right package name (starting with JHIpster applications path name) and make it available in class path
2. Gain access to view entity's audit changelogs (Role: ADMIN)
3. pass in the malicious class name part as `entityType` (first mentioned part) // `qualifiedName` (second mentioned occurence)
4. class gets loaded and static code blocks in there get executed

--> Should be limited to the already existing whitelist of classes (see first method in that mentioned class)

### Impact
Remote Code execution. You need to have some access to place malicious classes into the class path and you need to have a user with ADMIN role on the system.

## References
- https://github.com/jhipster/generator-jhipster-entity-audit/security/advisories/GHSA-7rmp-3g9f-cvq8
- https://nvd.nist.gov/vuln/detail/CVE-2025-31119
- https://github.com/jhipster/generator-jhipster-entity-audit
- https://github.com/jhipster/generator-jhipster-entity-audit/blob/e21e83135d10c77d92203c89cb0b0063914e8fe0/generators/spring-boot-javers/templates/src/main/java/_package_/web/rest/JaversEntityAuditResource.java.ejs#L88
