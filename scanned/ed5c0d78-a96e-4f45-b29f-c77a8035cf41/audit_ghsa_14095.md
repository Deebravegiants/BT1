# [M] Vert.x STOMP server process client frames that would not send initially a connect frame

## Summary
Severity: Medium
Advisory: GHSA-gvrq-cg5r-7chp
CVE: CVE-2023-32081
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-12
Source: https://github.com/advisories/GHSA-gvrq-cg5r-7chp
Type: github-advisory

## Affected
- Maven: `io.vertx:vertx-stomp` — affected >=3.1.0 <3.9.16
- Maven: `io.vertx:vertx-stomp` — affected >=4.0.0 <4.4.2

## Details
### Impact
A Vert.x STOMP server processes client STOMP frames without checking that the client send an initial CONNECT frame replied with a successful CONNECTED frame. The client can subscribe to a destination or publish message without prior authentication. Any Vert.x STOMP server configured with an authentication handler is impacted.

### Patches
The issue is patched in Vert.x 4.4.2 and Vert.x 3.9.16

### Workarounds
No trivial workaround.

## References
- https://github.com/vert-x3/vertx-stomp/security/advisories/GHSA-gvrq-cg5r-7chp
- https://nvd.nist.gov/vuln/detail/CVE-2023-32081
- https://github.com/vert-x3/vertx-stomp/commit/0de4bc5a44ddb57e74d92c445f16456fa03f265b
- https://github.com/vert-x3/vertx-stomp
