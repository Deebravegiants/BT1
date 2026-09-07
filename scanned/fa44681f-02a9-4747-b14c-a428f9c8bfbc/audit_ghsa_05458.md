# [M] Mailpit is vulnerable to Cross-Site WebSocket Hijacking (CSWSH) allowing unauthenticated access to emails

## Summary
Severity: Medium
Advisory: GHSA-524m-q5m7-79mm
CVE: CVE-2026-22689
CWE: CWE-1385
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-524m-q5m7-79mm
Type: github-advisory

## Affected
- Go: `github.com/axllent/mailpit` — affected >=1.2.6 <1.28.2
- Go: `github.com/axllent/mailpit` — affected >=0 <0.0.0-20260110031614

## Details
**Summary**
The Mailpit WebSocket server is configured to accept connections from any origin. This lack of Origin header validation introduces a Cross-Site WebSocket Hijacking (CSWSH) vulnerability.

An attacker can host a malicious website that, when visited by a developer running Mailpit locally, establishes a WebSocket connection to the victim's Mailpit instance (default ws://localhost:8025). This allows the attacker to intercept sensitive data such as email contents, headers, and server statistics in real-time.

**Vulnerable Code**
The vulnerability exists in server/websockets/client.go where the CheckOrigin function is explicitly set to return true for all requests, bypassing standard Same-Origin Policy (SOP) protections provided by the gorilla/websocket library.

https://github.com/axllent/mailpit/blob/877a9159ceeaf380d5bb0e1d84017b24d2e7b361/server/websockets/client.go#L34-L39

**Impact**
This vulnerability impacts the Confidentiality of the data stored in or processed by Mailpit.
Although Mailpit is often used as a local development tool, this vulnerability allows remote exploitation via a web browser.

- **Scenario**: A developer has Mailpit running at localhost:8025.
- **Trigger**: The developer visits a malicious website (or a compromised legitimate site) in the same browser.
- **Exploitation**: The malicious site's JavaScript initiates a WebSocket connection to ws://localhost:8025/api/events. Since the origin check is disabled, the browser allows this cross-origin connection.
- **Data Leak**: The attacker receives all broadcasted events, including full email details (subjects, sender/receiver info) and server metrics.

**Attack Impact**
- Real-time notification of new emails
- Email metadata (sender, subject, recipients)
- Mailbox statistics
- All WebSocket broadcast data

**Recommended Fix**
The `CheckOrigin` function should be removed to allow gorilla/websocket to enforce its default safe behavior (checking that the Origin matches the Host). Alternatively, strict validation logic should be implemented.

**Proposed Change (Remove unsafe check):**

```go
var upgrader = websocket.Upgrader{
    ReadBufferSize:    1024,
    WriteBufferSize:   1024,
    // CheckOrigin: func(r *http.Request) bool { return true }, // REMOVED
    EnableCompression: true,
}
```

**Proof of Concept (PoC)**: To reproduce this vulnerability:

- Start Mailpit (default settings).
- Save the following HTML code as poc.html and serve it from a different origin (e.g., using python http.server on port 8000 or opening it directly as a file).
- Open the [poc_websocket_hijack.html](https://github.com/user-attachments/files/24522726/poc_websocket_hijack.html) file in your browser.
- Send a test email to Mailpit or perform any action in the Mailpit UI.
- Observe that the "malicious" page successfully receives the event data.

## References
- https://github.com/axllent/mailpit/security/advisories/GHSA-524m-q5m7-79mm
- https://nvd.nist.gov/vuln/detail/CVE-2026-22689
- https://github.com/axllent/mailpit/commit/6f1f4f34c98989fd873261018fb73830b30aec3f
- https://github.com/axllent/mailpit
