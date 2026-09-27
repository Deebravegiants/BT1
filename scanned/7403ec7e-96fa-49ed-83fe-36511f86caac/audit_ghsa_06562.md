# [M] veraPDF-validatio: Use of Default `DocumentBuilderFactory` leads to XXE When Processing Untrusted PDFs

## Summary
Severity: Medium
Advisory: GHSA-cg9x-g3gm-h5h6
CVE: CVE-2026-54082
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-cg9x-g3gm-h5h6
Type: github-advisory

## Affected
- Maven: `org.verapdf:validation-model` — affected >=1.17.35 <1.30.2
- Maven: `org.verapdf:validation-model` — affected >=1.31.1 <1.31.71
- Maven: `org.verapdf:validation-model-jakarta` — affected >=1.17.35 <1.30.2
- Maven: `org.verapdf:validation-model-jakarta` — affected >=1.31.1 <1.31.71

## Details
### Summary

veraPDF-validation has an XML External Entity (XXE) vulnerability in two PDF parsing paths (validate and `GFPDAcroForm.getdynamicRender()`). A malicious/crafted PDF supplied to a veraPDF consumer can lead to the expansion of external entities while parsing rich-text annotation/form-field values or XFA configurations, allowing local file disclosure and potentially outbound network requests depending on the runtime (host) environment.

### Details

Consumers that utilise either the `PDFAValidator.validate(...)` or `GFPDAcroForm(acroForm).getdynamicRender()` APIs to process untrusted PDFs are vulnerable to XXE exploits. 

Both vulnerable paths share the same root cause: the underlying source binds a default `DocumentBuilderFactory` and immediately calls `newDocumentBuilder()` which does not disable parsing of DTDs, external entities, XInclude, or external resource access directives in XML schemas.

This is an XXE vulnerability affecting applications that use veraPDF's affected APIs to parse or validate untrusted PDFs.

An attacker could craft a PDF that includes crafted XML external entities that when processed by vulnerable consumers could lead to local file disclosure and server-side outbound requests to attacker-controlled endpoints, depending on JVM XML parser behavior and network controls on the host.

## References
- https://github.com/veraPDF/veraPDF-validation/security/advisories/GHSA-cg9x-g3gm-h5h6
- https://github.com/veraPDF/veraPDF-validation/pull/730
- https://github.com/veraPDF/veraPDF-validation/commit/94caa46c1a594512247fbd46c808edae39469542
- https://github.com/veraPDF/veraPDF-validation/commit/cacd9436d0de40b0e58cc7d2dbb06451619e61ec
- https://github.com/veraPDF/veraPDF-validation
