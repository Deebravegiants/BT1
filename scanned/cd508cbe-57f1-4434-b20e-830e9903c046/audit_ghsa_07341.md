# [H] veraPDF Validation XXE via Rich Text

## Summary
Severity: High
Advisory: GHSA-3jh7-wm29-q568
CVE: CVE-2026-54078
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-3jh7-wm29-q568
Type: github-advisory

## Affected
- Maven: `org.verapdf:validation-model` — affected >=1.25.73 <1.30.2
- Maven: `org.verapdf:validation-model` — affected >=1.31.1 <1.31.71
- Maven: `org.verapdf:validation-model-jakarta` — affected >=1.25.73 <1.30.2
- Maven: `org.verapdf:validation-model-jakarta` — affected >=1.31.1 <1.31.71

## Details
## Summary  
  
**Description**
An XML External Entity Injection (CWE-611) vulnerability in veraPDF allows a remote attacker to read arbitrary files on the server file system and perform Server-Side Request Forgery by submitting a crafted PDF containing a malicious rich-text (/RC or /RV) entry. This affects all current versions of veraPDF-validation.  
  
## Details  
The vulnerability resides in veraPDF-validation `validation-model/src/main/java/org/verapdf/gf/model/tools/DictionaryKeysHelper.java` within the `getRichTextStringOrStreamEntryStringRepresentation()` method. This helper extracts the XHTML rich-text body from a PDF dictionary string or stream and parses it with a DOM parser to return the concatenated text content.  
  
The vulnerability stems from two combined issues:  
- The DocumentBuilderFactory is instantiated with default settings , no disallow-doctype-decl, no disabling of external general/parameter entities, no FEATURE_SECURE_PROCESSING, and no secure EntityResolver. The default JAXP/Xerces parser will therefore resolve `<!DOCTYPE … SYSTEM "…">` and `<!ENTITY … SYSTEM "…">` declarations.  
- After parsing, `getAllNodeText()` recursively concatenates every text node in the document and returns it as the model property value. This means the expanded contents of any external entity are reflected directly back into the validation report.  
  
## Impact  
  
This impacts all current releases of the veraPDF validation-model module.  
  
Successful exploitation requires only that the target validate an attacker-supplied PDF. A single markup annotation with a crafted /RC string is sufficient.  
   
## Proposed Patch  
  
Harden the `DocumentBuilderFactory` in `validation-model/src/main/java/org/verapdf/gf/model/tools/DictionaryKeysHelper.java` per the OWASP XXE Prevention Cheat Sheet to disallow DOCTYPE outright.

## References
- https://github.com/veraPDF/veraPDF-validation/security/advisories/GHSA-3jh7-wm29-q568
- https://github.com/veraPDF/veraPDF-validation
