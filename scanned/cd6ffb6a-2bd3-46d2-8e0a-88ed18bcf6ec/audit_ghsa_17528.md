# [M] Jackson-core Vulnerable to Memory Disclosure via Source Snippet in JsonLocation

## Summary
Severity: Medium
Advisory: GHSA-wf8f-6423-gfxg
CVE: CVE-2025-49128
CWE: CWE-209
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-06-07
Source: https://github.com/advisories/GHSA-wf8f-6423-gfxg
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-core` — affected >=2.0.0 <2.13.0

## Details
### Overview

A flaw in Jackson-core's `JsonLocation._appendSourceDesc` method allows up to 500 bytes of unintended memory content to be included in exception messages. When parsing JSON from a byte array with an offset and length, the exception message incorrectly reads from the beginning of the array instead of the logical payload start. This results in possible **information disclosure** in systems using **pooled or reused buffers**, like Netty or Vert.x.

### Details

The vulnerability affects the creation of exception messages like:

```
JsonParseException: Unexpected character ... at [Source: (byte[])...]
```

When `JsonFactory.createParser(byte[] data, int offset, int len)` is used, and an error occurs while parsing, the exception message should include a snippet from the specified logical payload. However, the method `_appendSourceDesc` ignores the `offset`, and always starts reading from index `0`.

If the buffer contains residual sensitive data from a previous request, such as credentials or document contents, that data may be exposed if the exception is propagated to the client.

The issue particularly impacts server applications using:

* Pooled byte buffers (e.g., Netty)
* Frameworks that surface parse errors in HTTP responses
* Default Jackson settings (i.e., `INCLUDE_SOURCE_IN_LOCATION` is enabled)

A documented real-world example is [CVE-2021-22145](https://nvd.nist.gov/vuln/detail/CVE-2021-22145) in Elasticsearch, which stemmed from the same root cause.

### Attack Scenario

An attacker sends malformed JSON to a service using Jackson and pooled byte buffers (e.g., Netty-based HTTP servers). If the server reuses a buffer and includes the parser’s exception in its HTTP 400 response, the attacker may receive residual data from previous requests.

### Proof of Concept

```java
byte[] buffer = new byte[1000];
System.arraycopy("SECRET".getBytes(), 0, buffer, 0, 6);
System.arraycopy("{ \"bad\": }".getBytes(), 0, buffer, 700, 10);

JsonFactory factory = new JsonFactory();
JsonParser parser = factory.createParser(buffer, 700, 20);
parser.nextToken(); // throws exception

// Exception message will include "SECRET"
```

### Patches
This issue was silently fixed in jackson-core version 2.13.0, released on September 30, 2021, via [PR #652](https://github.com/FasterXML/jackson-core/pull/652).

All users should upgrade to version 2.13.0 or later.

### Workarounds
If upgrading is not immediately possible, applications can mitigate the issue by:

1. **Disabling exception message exposure to clients** — avoid returning parsing exception messages in HTTP responses.
2. **Disabling source inclusion in exceptions** by setting:

   ```java
   jsonFactory.disable(JsonFactory.Feature.INCLUDE_SOURCE_IN_LOCATION);
   ```

    This prevents Jackson from embedding any source content in exception messages, avoiding leakage.


### References
* [Pull Request #652 (Fix implementation)](https://github.com/FasterXML/jackson-core/pull/652)
* [CVE-2021-22145 (Elasticsearch exposure of this flaw)](https://nvd.nist.gov/vuln/detail/CVE-2021-22145)

## References
- https://github.com/FasterXML/jackson-core/security/advisories/GHSA-wf8f-6423-gfxg
- https://nvd.nist.gov/vuln/detail/CVE-2021-22145
- https://nvd.nist.gov/vuln/detail/CVE-2025-49128
- https://github.com/FasterXML/jackson-core/pull/652
- https://github.com/FasterXML/jackson-core/commit/a6c297682737dde13337cb7c3020f299518609a8
- https://github.com/FasterXML/jackson-core
