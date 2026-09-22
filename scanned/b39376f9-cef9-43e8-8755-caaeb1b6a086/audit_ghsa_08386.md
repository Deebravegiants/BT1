# [C] OpenMRS has Stored Velocity SSTI to RCE via ConceptReferenceRange

## Summary
Severity: Critical
Advisory: GHSA-xj4f-8jjg-vx4q
CVE: CVE-2026-41258
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-xj4f-8jjg-vx4q
Type: github-advisory

## Affected
- Maven: `org.openmrs.api:openmrs-api` — affected >=2.7.0 <2.7.9
- Maven: `org.openmrs.api:openmrs-api` — affected >=2.8.0 <2.8.6

## Details
### Impact

The `ConceptReferenceRangeUtility.evaluateCriteria()` method in OpenMRS Core
evaluates database-stored criteria strings as Apache Velocity templates without any sandbox configuration. The `VelocityEngine` is initialized with only logging properties and no`SecureUberspector`, leaving the default `UberspectImpl` in place, which allows
unrestricted Java reflection through template expressions.

A user with the `Manage Concepts` privilege can store a malicious Velocity template
expression in a concept's reference range criteria field. This payload is then executed
automatically whenever a user or API call validates an observation against the affected
concept. The Velocity context exposes `$patient` (the `Person` / `Patient` object), `$obs` (the `Obs` object), and `$fn` (the `ConceptReferenceRangeUtility` instance with access to the full OpenMRS service layer).

**Persistent Remote Code Execution**: The payload persists in the concept_reference_range database table (VARCHAR 65535). A single compromised concept for a common clinical measurement executes the payload on every subsequent observation validation across all users, API clients, and integrations in the facility.

**Privilege Escalation**: The Manage Concepts privilege is a content-management function, defined as "Able to add/edit/delete concept entries", not an administrative privilege. Multiple non-admin staff per facility typically hold this privilege. The attacker escalates from concept dictionary management to arbitrary code execution as the Tomcat application server process.

**PHI Exfiltration**: The Velocity context objects directly expose patient data without requiring OS-level RCE.

### Patches

This is fixed in 2.8.6 and 2.7.9 as well as future versions.

### Workarounds

Ensure the `Manage Concepts` privilege is restricted to only authorized users and carefully audit any `ConceptReferenceRanges` in the database.

### Resources
https://github.com/openmrs/openmrs-core/commit/8d1c193
https://www.machinespirits.com/advisory/1e8430/

## References
- https://github.com/openmrs/openmrs-core/security/advisories/GHSA-xj4f-8jjg-vx4q
- https://nvd.nist.gov/vuln/detail/CVE-2026-41258
- https://github.com/openmrs/openmrs-core/commit/8d1c193
- https://github.com/openmrs/openmrs-core
- https://www.machinespirits.com/advisory/1e8430
