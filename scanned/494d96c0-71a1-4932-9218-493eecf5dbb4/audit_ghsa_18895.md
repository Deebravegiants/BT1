# [H] CycloneDX Core (Java): BOM validation is vulnerable to XML External Entity injection 

## Summary
Severity: High
Advisory: GHSA-6fhj-vr9j-g45r
CVE: CVE-2025-64518
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-11-10
Source: https://github.com/advisories/GHSA-6fhj-vr9j-g45r
Type: github-advisory

## Affected
- Maven: `org.cyclonedx:cyclonedx-core-java` — affected >=2.1.0 <11.0.1

## Details
### Impact

The XML [`Validator`](https://docs.oracle.com/javase/8/docs/api/javax/xml/validation/Validator.html) used by cyclonedx-core-java was not configured securely, making the library vulnerable to XML External Entity (XXE) injection.

The fix for GHSA-683x-4444-jxh8 / CVE-2024-38374 has been incomplete in that it only fixed *parsing* of XML BOMs, but not *validation*.

### Patches

The vulnerability has been fixed in cyclonedx-core-java version 11.0.1.

### Workarounds

If feasible, applications can reject XML documents before handing them to cyclonedx-core-java for validation.
This may be an option if incoming CycloneDX BOMs are known to be in JSON format.

### References

* The issue was introduced via https://github.com/CycloneDX/cyclonedx-core-java/commit/162aa594f347b3f612fe0a45071693c3cd398ce9
* The issue was fixed via https://github.com/CycloneDX/cyclonedx-core-java/pull/737
* https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html#schemafactory

## References
- https://github.com/CycloneDX/cyclonedx-core-java/security/advisories/GHSA-6fhj-vr9j-g45r
- https://nvd.nist.gov/vuln/detail/CVE-2025-64518
- https://github.com/CycloneDX/cyclonedx-core-java/pull/737
- https://github.com/CycloneDX/cyclonedx-core-java/commit/162aa594f347b3f612fe0a45071693c3cd398ce9
- https://github.com/CycloneDX/cyclonedx-core-java/commit/af0ec75c93c03f93733a070c5132554490af5314
- https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html#schemafactory
- https://github.com/CycloneDX/cyclonedx-core-java
