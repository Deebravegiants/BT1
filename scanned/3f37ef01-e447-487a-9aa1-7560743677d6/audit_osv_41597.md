# [H] HAPI FHIR: JSON utility parser unbounded recursion causes StackOverflow denial of service

## Summary
Severity: High
Advisory: CVE-2026-62295
Aliases: GHSA-2cq7-hg49-56gc
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-62295
Type: osv

## Details
HAPI FHIR is a complete implementation of the HL7 FHIR standard for healthcare interoperability in Java. Prior to 6.9.11, the JSON utility parser in org.hl7.fhir.utilities.json.parser.JsonParser enforces no maximum nesting depth for arrays or objects. As a result, a small but deeply nested, syntactically valid FHIR JSON document can trigger unbounded readArray() or readObject() recursion, raising a StackOverflowError before structural validation runs. An attacker who can submit JSON resources for validation can thus crash the request thread, and services that do not isolate StackOverflowError safely may experience worker loss or process instability — a denial-of-service condition. This issue is fixed in version 6.9.11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62295.json
- https://github.com/hapifhir/org.hl7.fhir.core/security/advisories/GHSA-2cq7-hg49-56gc
- https://nvd.nist.gov/vuln/detail/CVE-2026-62295
- https://github.com/hapifhir/org.hl7.fhir.core/commit/396f447500407693d6ae1e64db59782862ca7506
