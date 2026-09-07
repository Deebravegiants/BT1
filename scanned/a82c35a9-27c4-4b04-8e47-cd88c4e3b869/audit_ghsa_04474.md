# [H] JLine3 Telnet server: Unauthenticated Remote Memory Exhaustion via Unbounded Telnet NEW-ENVIRON Variables

## Summary
Severity: High
Advisory: GHSA-47qp-hqvx-6r3f
CVE: CVE-2026-56740
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-47qp-hqvx-6r3f
Type: github-advisory

## Affected
- Maven: `org.jline:jline-remote-telnet` — affected >=4.1.0 <4.2.1
- Maven: `org.jline:jline-remote-telnet` — affected >=4.0.0 <4.0.16
- Maven: `org.jline:jline-remote-telnet` — affected >=0 <3.30.14

## Details
### Summary

The JLine3 Telnet server (`remote-telnet` module) does not limit the number of
environment variables a client may inject via the Telnet NEW-ENVIRON option. An
unauthenticated attacker can flood the server with a large number of unique
variable pairs before sending the terminating IAC SE byte, exhausting JVM heap
memory and causing an OutOfMemoryError (denial of service). Approximately 3–4 MB of
network traffic is sufficient to consume a 512 MB JVM heap.

### Details

`TelnetIO.readNEVariables()` (TelnetIO.java:1127-1180) processes incoming NEW-ENVIRON
variable pairs in a loop and stores each pair in a `HashMap` held by `ConnectionData`:

```java
// TelnetIO.java:1139-1178
boolean cont = true;
if (i == NE_VAR || i == NE_USERVAR) {
    do {
        switch (readNEVariableName(sbuf)) {
            case NE_VAR_OK:
                TelnetIO.this.connectionData.getEnvironment().put(str, sbuf.toString());
                // ← no per-connection count limit
                break;
            case NE_VAR_UNDEFINED:
                break; // cont remains true, loop continues
        }
    } while (cont);  // cont is never set to false; only exits via return
}
```

The variable accumulator map is a plain `HashMap` initialized with capacity 20 and
**no maximum size**:

```java
// ConnectionData.java:98
environment = new HashMap<String, String>(20);
```

Per-variable limits exist (name: max 50 chars, value: max 1000 chars), but there is no
cap on the *count* of variables. Each map entry occupies approximately 2 KB of heap
(String headers + `Map.Entry` + backing char arrays). On a JVM with a 512 MB heap,
approximately 250,000 unique entries trigger an `OutOfMemoryError`.

Network cost: using sequential 1-byte names (e.g., `\x01`, `\x02`, ...) and 1-byte
values, each variable pair requires roughly 13 protocol bytes. Sending 250,000 pairs
requires only ~3.25 MB of network traffic — feasible in seconds over any reasonable
network connection.

No authentication is required. NEW-ENVIRON negotiation occurs before login.

Affected source files:
- `remote-telnet/src/main/java/org/jline/builtins/telnet/TelnetIO.java` lines 1127-1180
- `remote-telnet/src/main/java/org/jline/builtins/telnet/ConnectionData.java` line 98

### PoC

Connect to the JLine3 Telnet server and, after completing WILL/DO option negotiation,
send a NEW-ENVIRON SEND subneg followed by a single large IS subneg containing
thousands of unique variable pairs before the final IAC SE.

Protocol structure (no authentication required):
1. Standard Telnet option negotiation (IAC DO NEW-ENVIRON, IAC WILL NEW-ENVIRON)
2. Server sends IAC SB NEW-ENVIRON SEND IAC SE
3. Client responds with: IAC SB NEW-ENVIRON IS
     [NE_VAR 0x01 NE_VALUE 0x01]  ← variable pair 1
     [NE_VAR 0x02 NE_VALUE 0x01]  ← variable pair 2
     ... repeated N times ...
     IAC SE                        ← only sent after N pairs

Each iteration adds one entry to the per-connection environment map. The connection
thread blocks reading from the socket while accumulating pairs, so the attacker
controls the timing of the OOM.

Reproduction environment:
- JLine3 built from current master on x86_64 Linux, OpenJDK 25.0.2
- `remote-telnet` module started with its default configuration
- Confirmed by source-code analysis; loop exit condition and missing count guard
  verified by inspection of `readNEVariables()` and `ConnectionData` constructor

### Impact

**Type**: Denial of Service (heap memory exhaustion / OutOfMemoryError)
**Who is affected**: Any application embedding the JLine3 `remote-telnet` module and
exposing its Telnet server. No credentials are required. A single connection can exhaust
the entire JVM heap, crashing the host process or triggering JVM out-of-memory
handling that impacts all users sharing that JVM instance.

### Credits 

This issue was identified by Michał Majchrowicz and Marcin Wyczechowski, members of the AFINE Team.

## References
- https://github.com/jline/jline3/security/advisories/GHSA-47qp-hqvx-6r3f
- https://nvd.nist.gov/vuln/detail/CVE-2026-56740
- https://github.com/jline/jline3/pull/2000
- https://github.com/jline/jline3/pull/2001
- https://github.com/jline/jline3/commit/0389f0ee6d0375901b602671ad5dafd4d1d4ee09
- https://github.com/jline/jline3/commit/4ee3a73849ffb9a85ec748e4e8cd8f6d81f84f40
- https://github.com/jline/jline3/commit/934f09e6128cee33c2b13d42b6e859c1ee2d194b
- https://github.com/jline/jline3
- https://github.com/jline/jline3/releases/tag/4.0.16
- https://github.com/jline/jline3/releases/tag/4.2.1
- https://github.com/jline/jline3/releases/tag/jline-3.30.14
