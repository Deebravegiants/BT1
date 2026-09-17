# [H] JLine3 Telnet server: Unauthenticated Remote DoS via Unbounded Telnet NAWS Terminal Geometry

## Summary
Severity: High
Advisory: GHSA-2r2c-cx56-8933
CVE: CVE-2026-56741
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-2r2c-cx56-8933
Type: github-advisory

## Affected
- Maven: `org.jline:jline-remote-telnet` — affected >=4.1.0 <4.2.1
- Maven: `org.jline:jline-remote-telnet` — affected >=4.0.0 <4.0.16
- Maven: `org.jline:jline-remote-telnet` — affected >=0 <3.30.14

## Details
### Summary

The JLine3 Telnet server (`remote-telnet` module) does not apply an upper bound to
terminal dimensions received via the Telnet NAWS (Negotiate About Window Size) option.
An unauthenticated remote attacker can send a NAWS subnegotiation advertising a
65535×65535 terminal and repeatedly alternate values to trigger continuous, expensive
rendering work on the server, causing CPU exhaustion and denial of service.

### Details

`TelnetIO.handleNAWS()` (TelnetIO.java:856-879) reads the client-supplied width and
height as 16-bit unsigned integers and passes them to `setTerminalGeometry()`:

```java
// TelnetIO.java:869-875
private void setTerminalGeometry(int columns, int rows) {
    if (columns < SMALLEST_BELIEVABLE_WIDTH) columns = DEFAULT_WIDTH;  // lower bound only
    if (rows    < SMALLEST_BELIEVABLE_HEIGHT) rows    = DEFAULT_HEIGHT;
    connectionData.setTerminalGeometry(columns, rows);
    connection.processConnectionEvent(
        new ConnectionEvent(connection, ConnectionEvent.Type.CONNECTION_TERMINAL_GEOMETRY_CHANGED));
}
```

Only a *lower* bound is enforced (minimum 20 columns / 6 rows). Values up to 65535 are
accepted and stored. The geometry change event propagates to Telnet.java:153-158 where
it calls:

    terminal.setSize(new Size(65535, 65535));
    terminal.raise(Signal.WINCH);

The WINCH signal triggers `LineReaderImpl.handleSignal()` → `redisplay()`. Inside
`redisplay()`, multiple paths iterate up to `size.getColumns()` times:

- `freshLine()` (LineReaderImpl.java:937,953): loops `size.getColumns()-1` = **65534
  iterations**, building and writing a space-padding string across the network socket.
- `columnSplitLength(terminal, size.getColumns(), ...)`: called multiple times,
  each processing all characters against the 65535-wide line width.

Because WINCH only fires on *change*, the attacker alternates between two large values
(e.g., 65535 and 65534) to trigger an unlimited stream of expensive render cycles.
No authentication is required; the NAWS option is negotiated before any login sequence.

Affected source files:
- `remote-telnet/src/main/java/org/jline/builtins/telnet/TelnetIO.java` lines 856-879
- `remote-telnet/src/main/java/org/jline/builtins/telnet/Telnet.java` lines 140-175
- `reader/src/main/java/org/jline/reader/impl/LineReaderImpl.java` lines 929-962, 1293-1313

### PoC

Send the following two raw Telnet packets in a loop to a running JLine Telnet server.
No login or authentication is required.

Packet 1 — NAWS 65535 × 65535:
  FF FA 1F FF FF FF FF FF F0
  (IAC SB NAWS 0xFF 0xFF 0xFF 0xFF IAC SE)

Packet 2 — NAWS 65534 × 65534:
  FF FA 1F FF FE FF FE FF F0
  (IAC SB NAWS 0xFF 0xFE 0xFF 0xFE IAC SE)

Sending these alternately at ~10 packets/second is sufficient to peg one CPU core on
the server. The server remains in this state for as long as the connection is open.

Reproduction environment:
- JLine3 built from current master on x86_64 Linux, OpenJDK 25.0.2
- `remote-telnet` module started with its default `Telnet` server configuration
- Test confirmed by source-code analysis and tracing the call chain at runtime

### Impact

**Type**: Denial of Service (CPU exhaustion)
**Who is affected**: Any application that embeds the JLine3 `remote-telnet` module and
exposes its Telnet server on a network interface. The attacker requires no credentials.
A single connection making ~10 alternating NAWS packets per second fully occupies the
connection-handling thread and produces continuous I/O on the server's output stream.
Because connection threads are re-used for the life of the session, one attacker per
available connection slot can deny service to all users of that slot.

### Credits
This issue was identified by Michał Majchrowicz and Marcin Wyczechowski, members of the AFINE Team.

## References
- https://github.com/jline/jline3/security/advisories/GHSA-2r2c-cx56-8933
- https://nvd.nist.gov/vuln/detail/CVE-2026-56741
- https://github.com/jline/jline3/pull/2000
- https://github.com/jline/jline3/commit/3ea9cad8699714dc072fade29d36be0d1e23d708
- https://github.com/jline/jline3/commit/733eb353dca7b0ea0252e724445b6defa29c393e
- https://github.com/jline/jline3/commit/86b7ba7801988aadb1a67555629522a71d603bd3
- https://github.com/jline/jline3
- https://github.com/jline/jline3/releases/tag/4.0.16
- https://github.com/jline/jline3/releases/tag/4.2.1
