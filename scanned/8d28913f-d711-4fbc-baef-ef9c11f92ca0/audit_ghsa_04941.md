# [H] HAPI FHIR: Incomplete fix for CVE-2026-45367: DSTU2 FHIRPathEngine.matches() missing RegexTimeout protection allows ReDoS

## Summary
Severity: High
Advisory: GHSA-fxj4-p9xp-37v5
CVE: CVE-2026-55470
CWE: CWE-1333
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-fxj4-p9xp-37v5
Type: github-advisory

## Affected
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.dstu2` — affected >=0 <6.9.10
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.convertors` — affected >=0 <6.9.10
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.validation` — affected >=0 <6.9.10
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.validation.cli` — affected >=0 <6.9.10

## Details
## Summary
The fix for CVE-2026-45367 added `RegexTimeout` protection to the `matches()` function in DSTU2016MAY, DSTU3, R4, R4B, and R5, but the DSTU2 module was incompletely patched. In `org.hl7.fhir.dstu2`, `replaceMatches()` was updated while `matches()` at line 2462 still calls the raw `String.matches(sw)` without any timeout, allowing an unauthenticated attacker to trigger catastrophic regex backtracking and exhaust server CPU.


## Details
### Incomplete patch

Within the same file
(`org.hl7.fhir.dstu2/utils/FHIRPathEngine.java`), the two functions were
patched inconsistently:

**Line 2226 — replaceMatches() — PATCHED:**
```java
result.add(new StringType(
    RegexTimeout.replaceAll(
        convertToString(focus.get(0)), regex, repl, regexTimeoutMillis)));
```

**Line 2462 — matches() — NOT PATCHED:**
```java
result.add(new BooleanType(
    convertToString(focus.get(0)).matches(sw)));
// ↑ raw String.matches() — no RegexTimeout, no complexity check
```

**DSTU3 line 2447 — matches() — PATCHED (for comparison):**
```java
result.add(new BooleanType(
    RegexTimeout.matches(st, sw, regexTimeoutMillis)));
```

### Module-by-module status

| Module | `matches()` | `replaceMatches()` |
|---|---|---|
| **DSTU2** | ❌ raw `str.matches(sw)` | ✅ `RegexTimeout.replaceAll()` |
| DSTU2016MAY | ✅ `RegexTimeout.matches()` | ✅ |
| DSTU3 | ✅ `RegexTimeout.matches()` | ✅ |
| R4 | ✅ `RegexTimeout.matches()` | ✅ |
| R4B | ✅ `RegexTimeout.matches()` | ✅ |
| R5 | ✅ `RegexTimeout.matches()` | ✅ |


## PoC
**Requirements:** Java 17+, Maven 3.8+

**pom.xml dependencies:**
```xml
<dependency>
    <groupId>ca.uhn.hapi.fhir</groupId>
    <artifactId>org.hl7.fhir.utilities</artifactId>
    <version>6.9.7</version>
</dependency>
```

**Test code (reproduces the exact behaviour of DSTU2 line 2462):**
```java
import org.hl7.fhir.utilities.regex.RegexTimeout;
import java.util.concurrent.*;

String regex = "((a|b){0,5}){20}";
String input = "a".repeat(25) + "c";    // no match → full backtracking

// ① Patched approach — RegexTimeout terminates at 500 ms
long t1 = System.currentTimeMillis();
try {
    RegexTimeout.matches(input, regex, 500);
} catch (TimeoutException e) {
    System.out.println("RegexTimeout blocked in " +
        (System.currentTimeMillis() - t1) + " ms");
}

// ② DSTU2 line 2462 — raw String.matches(), no timeout
long t2 = System.currentTimeMillis();
input.matches(regex);                   // equivalent to what FHIRPathEngine does
System.out.println("str.matches() ran for " +
    (System.currentTimeMillis() - t2) + " ms with no timeout");
```

**Verified output (JDK 25.0.3, Linux):**
```
RegexTimeout blocked in 508 ms      ← patched modules: attack stopped
str.matches() ran for 1410 ms       ← DSTU2: no timeout, CPU exhausted
```

The patched approach cuts off the evaluation at 508 ms. The unpatched DSTU2
code runs for 1410 ms on this input with no mechanism to stop it. Longer
inputs or more complex patterns produce proportionally worse results.


## Impact
**Vulnerability type:** Regular Expression Denial of Service (ReDoS) causing CPU exhaustion and service disruption.

**Who is impacted:** Any application using the `ca.uhn.hapi.fhir:org.hl7.fhir.dstu2` module that evaluates user-supplied FHIRPath expressions — including the FHIR Validator HTTP endpoint, FHIR servers applying FHIRPath invariants from user-provided resources or profiles, and any system embedding `FHIRPathEngine` from the DSTU2 module. No authentication is required; an attacker needs only to submit a FHIR resource or FHIRPath expression whose `matches()` argument contains a catastrophically backtracking regular expression.

## References
- https://github.com/hapifhir/org.hl7.fhir.core/security/advisories/GHSA-fxj4-p9xp-37v5
- https://github.com/hapifhir/org.hl7.fhir.core
