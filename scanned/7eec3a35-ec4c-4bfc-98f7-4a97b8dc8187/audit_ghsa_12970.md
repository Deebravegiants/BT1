# [M] DDFFileParser is vulnerable to XXE Attacks

## Summary
Severity: Medium
Advisory: GHSA-wc9j-gc65-3cm7
CVE: CVE-2023-41034
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-08-31
Source: https://github.com/advisories/GHSA-wc9j-gc65-3cm7
Type: github-advisory

## Affected
- Maven: `org.eclipse.leshan:leshan-core` — affected >=0 <1.5.0
- Maven: `org.eclipse.leshan:leshan-core` — affected >=2.0.0-M1 <2.0.0-M13

## Details
### Impact
`DDFFileParser` and `DefaultDDFFileValidator` (and so `ObjectLoader`) are vulnerable to [XXE Attacks](https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing).

[DDF file](https://github.com/eclipse-leshan/leshan/wiki/Adding-new-objects#the-lwm2m-model) is a LWM2M format used to store LWM2M object description.   
Leshan users are impacted only if they parse untrusted DDF files (e.g. if they let external users provide their own model), in that case they MUST upgrade to fixed version.
If you parse only trusted DDF file and validate only with trusted xml schema, upgrading is not mandatory. 

### Patches
This is fixed in **v1.5.0** and **2.0.0-M13**.

### Workarounds
No easy way. Eventually writing your own `DDFFileParser`/`DefaultDDFFileValidator` (and so `ObjectLoader`) creating a `DocumentBuilderFactory` with : 
```java
// For DDFFileParser
DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
factory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true); // Disable DTDs
factory.setXIncludeAware(false); // Disable XML Inclusions
factory.setExpandEntityReferences(false); // disable expand entity reference nodes

// For DefaultDDFFileValidator
SchemaFactory factory = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);
factory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
factory.setProperty(XMLConstants.ACCESS_EXTERNAL_DTD, "");
factory.setProperty(XMLConstants.ACCESS_EXTERNAL_SCHEMA, "");
``` 

### References
- https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing
- https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html
- https://semgrep.dev/docs/cheat-sheets/java-xxe/
- https://community.veracode.com/s/article/Java-Remediation-Guidance-for-XXE

## References
- https://github.com/eclipse-leshan/leshan/security/advisories/GHSA-wc9j-gc65-3cm7
- https://nvd.nist.gov/vuln/detail/CVE-2023-41034
- https://github.com/eclipse-leshan/leshan/commit/29577d2879ba8e7674c3b216a7f01193fc7ae013
- https://github.com/eclipse-leshan/leshan/commit/4d3e63ac271a817f81fba3e3229c519af7a3049c
- https://github.com/eclipse-leshan/leshan
- https://github.com/eclipse-leshan/leshan/wiki/Adding-new-objects#the-lwm2m-model
- https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing
