# [H] Improper Restriction of XML External Entity Reference in org.cyclonedx:cyclonedx-core-java

## Summary
Severity: High
Advisory: GHSA-683x-4444-jxh8
CVE: CVE-2024-38374
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-24
Source: https://github.com/advisories/GHSA-683x-4444-jxh8
Type: github-advisory

## Affected
- Maven: `org.cyclonedx:cyclonedx-core-java` — affected >=2.1.0 <9.0.4

## Details
### Impact

Before deserializing CycloneDX Bill of Materials in XML format, _cyclonedx-core-java_ leverages XPath expressions to determine the schema version of the BOM. The `DocumentBuilderFactory` used to evaluate XPath expressions was not configured securely, making the library vulnerable to XML External Entity (XXE) injection.

XXE injection can be exploited to exfiltrate local file content, or perform Server Side Request Forgery (SSRF) to access infrastructure adjacent to the vulnerable application.

### PoC

```java
import org.cyclonedx.parsers.XmlParser;

class Poc {

    public static void main(String[] args) {
        // Will throw org.cyclonedx.exception.ParseException: java.net.ConnectException: Connection refused
        new XmlParser().parse("""
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE bom [<!ENTITY % sp SYSTEM "https://localhost:1010/does-not-exist/file.dtd"> %sp;]>
            <bom xmlns="http://cyclonedx.org/schema/bom/1.5"/>
            """.getBytes());
    }

}
```

### Patches

The vulnerability has been fixed in _cyclonedx-core-java_ version 0.9.4.

### Workarounds

If feasible, applications can reject XML documents before handing them to _cyclonedx-core-java_ for parsing.
This may be an option if incoming CycloneDX BOMs are known to be in JSON format.

### References

* Issue was fixed via <https://github.com/CycloneDX/cyclonedx-core-java/pull/434>
* Issue was introduced via <https://github.com/CycloneDX/cyclonedx-core-java/commit/162aa594f347b3f612fe0a45071693c3cd398ce9>
* <https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing>
* <https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html#xpathexpression>

## References
- https://github.com/CycloneDX/cyclonedx-core-java/security/advisories/GHSA-683x-4444-jxh8
- https://nvd.nist.gov/vuln/detail/CVE-2024-38374
- https://github.com/CycloneDX/cyclonedx-core-java/pull/434
- https://github.com/CycloneDX/cyclonedx-core-java/pull/434/commits/ab0bc9c530d24f737970dbd0287d1190b129853d
- https://github.com/CycloneDX/cyclonedx-core-java
