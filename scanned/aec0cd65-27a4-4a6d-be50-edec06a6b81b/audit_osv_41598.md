# [H] HAPI FHIR: XHTML narrative parser unbounded recursion causes StackOverflow denial of service

## Summary
Severity: High
Advisory: CVE-2026-62296
Aliases: GHSA-5v24-q6x8-hc38
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-62296
Type: osv

## Details
HAPI FHIR is a complete implementation of the HL7 FHIR standard for healthcare interoperability in Java. Prior to 6.9.11, XhtmlParser.java imposes no maximum element nesting depth, so a deeply nested text.div narrative triggers unbounded recursion between parseElementInner() and parseElement(), raising a StackOverflowError. An attacker who can submit FHIR resources containing such narratives can thus crash a parsing or validation worker thread, affecting validator services and any application that parses attacker-supplied FHIR JSON or XML. This issue is fixed in version 6.9.11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62296.json
- https://github.com/hapifhir/org.hl7.fhir.core/security/advisories/GHSA-5v24-q6x8-hc38
- https://nvd.nist.gov/vuln/detail/CVE-2026-62296
- https://github.com/hapifhir/org.hl7.fhir.core/commit/396f447500407693d6ae1e64db59782862ca7506
