# [H] veraPDF Validation XXE via XFA

## Summary
Severity: High
Advisory: GHSA-36mm-w85j-3q2j
CVE: CVE-2026-54079
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-36mm-w85j-3q2j
Type: github-advisory

## Affected
- Maven: `org.verapdf:validation-model` — affected >=1.17.35 <1.30.2
- Maven: `org.verapdf:validation-model` — affected >=1.31.1 <1.31.71
- Maven: `org.verapdf:validation-model-jakarta` — affected >=1.17.35 <1.30.2
- Maven: `org.verapdf:validation-model-jakarta` — affected >=1.31.1 <1.31.71

## Details
## Summary  
  
**Description**
An XML External Entity Injection (CWE-611) vulnerability in veraPDF allows a remote attacker to read arbitrary files on the server file system and perform Server-Side Request Forgery by submitting a crafted PDF containing a malicious XFA stream. This affects all current versions of veraPDF-validation.  
  
## Details  
The vulnerability resides in veraPDF-validation `validation-model/src/main/java/org/verapdf/gf/model/impl/pd/GFPDAcroForm.java` within the `getdynamicRender()` method. This method retrieves the /XFA entry from the PDF's /AcroForm dictionary, decodes the embedded XML stream, and parses it to extract the `<dynamicRender>` element value.  
  
The vulnerability stems from the use of a default-configured `DocumentBuilderFactory` to parse fully attacker-controlled XML:  
- The factory is created via `DocumentBuilderFactory.newInstance()` with no security features enabled. disallow-doctype-decl, external-general-entities, external-parameter-entities, and FEATURE_SECURE_PROCESSING are all left at their insecure defaults.  
- The input passed to `builder.parse()` is the decoded /XFA stream taken directly from the untrusted PDF.  
- The text content of the `<dynamicRender>` node is returned to the validation model. Note that the shipped PDF/UA-1 rule (`dynamicRender != 'required'`) consumes this value but does not echo it into the report output, so reliable exfiltration requires the out-of-band parameter-entity technique described under Impact rather than in-band reflection.  
  
## Impact  
  
This impacts all current releases of the veraPDF validation-model module.  
  
Successful exploitation requires only that the target validate an attacker-supplied PDF against the PDF/UA-1 profile (or via flavour auto-detection on a PDF that declares PDF/UA-1 conformance), since `getdynamicRender()` is invoked by the `dynamicRender != 'required'` rule in the bundled PDF/UA-1 profile. No additional configuration or operator action is required.  
    
## Proposed Patch  
  
Harden the `DocumentBuilderFactory` in `validation-model/src/main/java/org/verapdf/gf/model/impl/pd/GFPDAcroForm.java` per the OWASP XXE Prevention Cheat Sheet to disallow DOCTYPE outright.

## References
- https://github.com/veraPDF/veraPDF-validation/security/advisories/GHSA-36mm-w85j-3q2j
- https://github.com/veraPDF/veraPDF-validation/pull/730
- https://github.com/veraPDF/veraPDF-validation/commit/94caa46c1a594512247fbd46c808edae39469542
- https://github.com/veraPDF/veraPDF-validation/commit/cacd9436d0de40b0e58cc7d2dbb06451619e61ec
- https://github.com/veraPDF/veraPDF-validation
