# [H] Jackson Core: Document length constraint bypass in blocking, async, and DataInput parsers

## Summary
Severity: High
Advisory: GHSA-2m67-wjpj-xhg9
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-2m67-wjpj-xhg9
Type: github-advisory

## Affected
- Maven: `tools.jackson.core:jackson-core` — affected >=3.0.0 <3.1.1

## Details
## Summary

Jackson Core 3.x does not consistently enforce `StreamReadConstraints.maxDocumentLength`. Oversized JSON documents can be accepted without a `StreamConstraintsException` in multiple parser entry points, which allows configured size limits to be bypassed and weakens denial-of-service protections.

## Details

Three code paths where `maxDocumentLength` is not fully enforced:

### 1. Blocking parsers skip validation of the final in-memory buffer

Blocking parsers validate only previously processed buffers, not the final in-memory buffer:

- `ReaderBasedJsonParser.java:255`
- `UTF8StreamJsonParser.java:208`

Relevant code:

```java
_currInputProcessed += bufSize;
_streamReadConstraints.validateDocumentLength(_currInputProcessed);
```

This means the check occurs only when a completed buffer is rolled over. If an oversized document is fully contained in the final buffer, parsing can complete without any document-length exception.

### 2. Async parsers skip validation of the final chunk on end-of-input

Async parsers validate previously processed chunks, but do not validate the final chunk on end-of-input:

- `NonBlockingByteArrayJsonParser.java:49`
- `NonBlockingByteBufferJsonParser.java:57`
- `NonBlockingUtf8JsonParserBase.java:75`

Relevant code:

```java
_currInputProcessed += _origBufferLen;
_streamReadConstraints.validateDocumentLength(_currInputProcessed);

public void endOfInput() {
    _endOfInput = true;
}
```

`endOfInput()` marks EOF but does not perform a final `validateDocumentLength(...)` call, so an oversized last chunk is accepted.

### 3. DataInput parser path does not enforce `maxDocumentLength` at all

- `JsonFactory.java:457`

Relevant construction path:

```java
int firstByte = ByteSourceJsonBootstrapper.skipUTF8BOM(input);
return new UTF8DataInputJsonParser(readCtxt, ioCtxt,
        readCtxt.getStreamReadFeatures(_streamReadFeatures),
        readCtxt.getFormatReadFeatures(_formatReadFeatures),
        input, can, firstByte);
```

`UTF8DataInputJsonParser` does not call `StreamReadConstraints.validateDocumentLength(...)`, so `maxDocumentLength` is effectively disabled for `createParser(..., DataInput)` users.

> **Note:** This issue appears distinct from the recently published nesting-depth and number-length constraint advisories because it affects document-length enforcement.

## PoC

### Async path reproducer

```java
import java.nio.charset.StandardCharsets;
import tools.jackson.core.JsonParser;
import tools.jackson.core.ObjectReadContext;
import tools.jackson.core.StreamReadConstraints;
import tools.jackson.core.async.ByteArrayFeeder;
import tools.jackson.core.json.JsonFactory;

public class Poc {
    public static void main(String[] args) throws Exception {
        JsonFactory factory = JsonFactory.builder()
                .streamReadConstraints(StreamReadConstraints.builder()
                        .maxDocumentLength(10L)
                        .build())
                .build();

        byte[] doc = "{\"a\":1,\"b\":2}".getBytes(StandardCharsets.UTF_8);

        try (JsonParser p = factory.createNonBlockingByteArrayParser(ObjectReadContext.empty())) {
            ByteArrayFeeder feeder = (ByteArrayFeeder) p.nonBlockingInputFeeder();
            feeder.feedInput(doc, 0, doc.length);
            feeder.endOfInput();

            while (p.nextToken() != null) { }
        }

        System.out.println("Parsed successfully");
    }
}
```

- **Expected result:** Parsing should fail because the configured document-length limit is 10, while the input is longer than 10 bytes.
- **Actual result:** The document is accepted and parsing completes.

### Blocking path reproducer

```java
import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import tools.jackson.core.JsonParser;
import tools.jackson.core.StreamReadConstraints;
import tools.jackson.core.json.JsonFactory;

public class Poc2 {
    public static void main(String[] args) throws Exception {
        JsonFactory factory = JsonFactory.builder()
                .streamReadConstraints(StreamReadConstraints.builder()
                        .maxDocumentLength(10L)
                        .build())
                .build();

        byte[] doc = "{\"a\":1,\"b\":2}".getBytes(StandardCharsets.UTF_8);

        try (JsonParser p = factory.createParser(new ByteArrayInputStream(doc))) {
            while (p.nextToken() != null) { }
        }

        System.out.println("Parsed successfully");
    }
}
```

## Impact

Applications that rely on `maxDocumentLength` as a safety control for untrusted JSON can accept oversized inputs without error. In network-facing services this weakens an explicit denial-of-service protection and can increase CPU and memory consumption by allowing larger-than-configured request bodies to be processed.

## References
- https://github.com/FasterXML/jackson-core/security/advisories/GHSA-2m67-wjpj-xhg9
- https://github.com/FasterXML/jackson-core/commit/74c9ee255d1534c179bc7d3de48941bf39a9079c
- https://github.com/FasterXML/jackson-core
